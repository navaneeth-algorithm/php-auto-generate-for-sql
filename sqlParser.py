'''

----This code is written by Navaneeth B------

    This is python code which will auto generate the 
    PHP object Oriented Query for Insert Statement,Execute Statement for given table
    Also the Ajax Query to send to the data to the Server side

    My Code takes MySQL file and grabs the information like 
    Table Names,Table Attributes ,and generate table Attributes, PHP and Ajax code
    which will  make web developer task easier
'''


import re
import enum
import string
import os.path
from os import path

#Clean the String from unwhanted character
class CleaningString:
    def cleaningString(self,sourceString,cleaningFrom):
        cleanedString = sourceString.translate(str.maketrans('','',cleaningFrom))
        return cleanedString


#Key Words for MySQL files 
class MySQLKeyWords:
    def __init__(self):
        #DataTypes
        self.__integerTypes = ["TINYINT","SMALLINT","MEDIUMINT","INT","BIGINT"]
        self.__floatingTypes = ["FLOAT","DOUBLE"]
        self.__fixedpointTypes=["DECIMAL","NUMERIC"]
        self.__bitvalueTypes = ["BIT"]
        self.__numericTypes = ["TYPE(N),ZEROFILL"]
        self.__datetimeTypes = ["DATETIME","DATE","TIMESTAMP"]
        self.__charTypes = ["CHAR","VARCHAR"]
        self.__binaryTypes = ["BINARY","VARBINARY"]
        self.__blobTypes = ["BLOB","TINYBLOB","MEDIUMBLOB","LONGBLOB"]
        self.__textTypes = ["TEXT","LONGTEXT","MEDIUMTEXT","TINYTEXT"]
        self.__enumtypes = ["ENUM"]
        self.__setTypes  = ["SET"]

        self.__alldataTypes = ["TINYINT","SMALLINT","MEDIUMINT","INT","BIGINT","FLOAT","DOUBLE"
        "DECIMAL","NUMERIC","BIT","TYPE(N),ZEROFILL","DATETIME","DATE","TIMESTAMP",
        "CHAR","VARCHAR","BINARY","VARBINARY","BLOB","TINYBLOB","MEDIUMBLOB","LONGBLOB","TEXT","LONGTEXT","MEDIUMTEXT","TINYTEXT",
        "ENUM","SET"]

        #KEY WORDS
        self.__keyword =["FOREIGN","PRIMARY","KEY","REFERENCES","CONSTRAINT",")","(","UNIQUE"] 
        pass

    def getKeyWord(self):
        return self.__keyword

#Parse the SQL File and store the tables as keys where value for those key is its parameters
class TableExtraction:
    def __init__(self,fileName):

        self.__sqlFileRead= open(fileName)
        self.__tableQueryData = dict()
        self.__tableParamters = list()
        
        self.__tableQuery()
        

    def __tableQuery(self):
        for lines in self.__sqlFileRead:
            tableName = ''

            #Finding Create Table Query
            if re.findall('CREATE TABLE',lines):

                #Extracting table name from the Query 
                tableName = lines.split(' ')[2]

                #cleaning the table name other than alphabets
                newTableName = tableName.translate(str.maketrans('','','``\n'))
                

                attributList = list()
                for queryLine in self.__sqlFileRead:
                    attributList.append(queryLine.strip())
                    if re.findall('^[)]',queryLine):
                        break
                #Adding Attribute list to Table Parameters

                self.__tableParamters.append(attributList)
                

                self.__tableQueryData[newTableName] = self.__tableParamters.copy()
                self.__tableParamters.clear()
    
    def getAttributeList(self,tableName):
        
        return self.__tableQueryData[tableName]
    
    def getTableNames(self):
        return list(self.__tableQueryData.keys())



#Here this Class parse the Extracted table and gives the Attributes of the table
class AttributeExtraction:
    def __init__(self,tableObject,tableName):
        self.__mySqlDataTypes = []
        self.__tableName = tableName
        self.__attributeList = tableObject.getAttributeList(tableName)[0]
        self.__keywordList = MySQLKeyWords().getKeyWord()
        #print(self.__keywordList)
        self.__attributes = list()
        self.__attributeTypePairing = dict()
        self.__attributeListParsing()
    
    def getTableName(self):
        return self.__tableName


    def __attributeListParsing(self):
        for i in self.__attributeList:
            queryList = i.split(' ')
            #print(queryList)
            if not queryList[0] in self.__keywordList:
                self.__attributes.append(queryList[0])
                self.__attributeTypePairing[queryList[0]] = queryList[1]
        pass

    def getAttribute(self):
        return self.__attributes
    
    def getAttributeType(self):
        return self.__attributeTypePairing

#This is  ENUM class
class TableQuery(enum.Enum):
    #defining Query of the Table
    CREATE = 0
    INSERT = 1
    DELETE = 2

#Generate the Queries for PHP according to  object based PHP
class GeneratePHPMySQLQuery:
    def __init__(self,attributeObj):
        self.__attributeList = attributeObj.getAttribute()
        self.__tableName = attributeObj.getTableName()
        self.__ajaxTemplate=""
        self .__insertTemplate = "include('dbConnect.php');\n//Coming from the Client Side i.e from form See output of Ajax Code Generation \n//Generated by the python Code sqlParser.py\n$data = $_POST['data'];\n$conn = $pdo->open();\n$query='INSERT INTO `"+self.__tableName+"`("
        self.__executeTemplate = "\n$stmt=$conn->prepare($query);\n$stmt->execute(["
        
        self.__insertQuery()
        self.__executeStatement()
        self.__ajaxJquery()
        pass

   
    def createConnectionTemplateFile(self):
        templateDbConnect = '''<?php
//Generated by the python code  sqlParser.py
#Replace hostname,databasename,username,password
Class Database{
    private $server = "mysql:host=hostname;dbname=databasename";
    private $username = "username";
    private $password = "password";
    private $options  = array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,);
    protected $conn;
    public function open(){
                try{
                    $this->conn = new PDO($this->server, $this->username, $this->password, $this->options);
                    return $this->conn;
                    }
                    catch(PDOException $e){
                    echo "There is some problem in connection: " . $e->getMessage();
                    } 
                }
                        
                public function close(){
                    $this->conn = null;
                 }
        }

        $pdo = new Database();


?>
 '''
        if not path.exists("dbConnect.php"):
            writeTemplate = open('dbConnect.php','w')
            writeTemplate.write(templateDbConnect)
            writeTemplate.close()
        else:
            print("File already Exists")
        

        pass

    def __ajaxJquery(self):
        varnameDeclaration = "function sendtoServer(){\nvar data={}\n"
        self.__ajaxTemplate+=varnameDeclaration
        for inputId in self.__attributeList:
            cleanedInputId = self.__tableName.lower()+CleaningString().cleaningString(inputId,'`')
            self.__ajaxTemplate+='data["'+cleanedInputId.lower()+'"]=$("#'+cleanedInputId.lower()+'").val();\n'
            pass
        self.__ajaxTemplate+="\n\n"
        self.__ajaxTemplate+="$.ajax({\n url:pathtoserverfile,\ndataType:'json'\ndata:{data:data},\ntype:POST,\n"
        self.__ajaxTemplate+="success:function(responses){ \nconsole.log(responses)\n},\n});\n}"


        pass
    
    def __insertQuery(self):
        #first step creating Attribute name
        count = 1
        for attributeName in self.__attributeList:
            separator = ','
            if(count==len(self.__attributeList)):
                separator=''
            self.__insertTemplate+=""+attributeName+separator
            count+=1
        self.__insertTemplate+=") VALUES("

        #creating attribute value alias
        count = 1
        for attributeAlias in self.__attributeList:
            lowerCaseAlias = str(self.__tableName).lower()+str(attributeAlias).lower()
            cleanedlowercaseAlias =CleaningString().cleaningString(lowerCaseAlias,'`')
            separator = ','
            if(count==len(self.__attributeList)):
                separator=''
            count+=1
            self.__insertTemplate+=":"+cleanedlowercaseAlias+separator
        
        self.__insertTemplate+=")';"
        pass

    def __executeStatement(self):
        count = 1
        for attributeAlias in self.__attributeList:
            varname = '$data["'
            lowerCaseAlias = str(self.__tableName).lower()+str(attributeAlias).lower()
            cleanedlowercaseAlias =CleaningString().cleaningString(lowerCaseAlias,'`')
            separator = ','
            if(count==len(self.__attributeList)):
                separator=''
            count+=1
            self.__executeTemplate+="'"+cleanedlowercaseAlias+"'=>"+varname+cleanedlowercaseAlias+'"]'+separator
        
        self.__executeTemplate+="]);\n$pdo->close();"
        pass
    

    def createPHPQueryFile(self):

        tableExtraction = TableExtraction('autophp.sql')
        attributes = AttributeExtraction(tableExtraction,"Client")
        phpgenerator= GeneratePHPMySQLQuery(attributes)

        fileString = '<?php \n'+phpgenerator.getInsertQuery()
        fileString+=phpgenerator.getExecuteStatement()+"\n?>"
        fileName = self.__tableName+".php"

        if not path.exists(fileName):
            writeTemplate = open(fileName,'w')
            writeTemplate.write(fileString)
            writeTemplate.close()
        else:
            print("File already Exists")
        pass 


    def getInsertQuery(self):
        return self.__insertTemplate
    
   
    def getAjaxCode(self):
        return self.__ajaxTemplate

    def getExecuteStatement(self):
        return self.__executeTemplate



#Takes TableExtraction takes the SQL file
#has useful methods to display TableNames
tableExtraction = TableExtraction('autophp.sql')

#gives the list of Table present in the SQL file

print("\n-----List of Table Names in autophp SQL file---------\n")
print(tableExtraction.getTableNames())

print("\n-------Attributes of the Table Client--------\n")

#Attribute Extraction takes TableExtraction object and the tableName
attributes = AttributeExtraction(tableExtraction,"Client")

#has useful methods like
#This will return the list of Attributes present in table

print(attributes.getAttribute())

print("\n---------Attributes with their DataTypes-----\n")
#This will return the list of attribute with their data type
print(attributes.getAttributeType())


print("\n------Generate the Ajax Code based on the Attributes of the table--------\n")
#This will take the attrbute object and useful methods 
phpgenerator= GeneratePHPMySQLQuery(attributes)

#It gives the ajax code based on the attributes present in the table
print(phpgenerator.getAjaxCode())


print("\n------Generate the Insert Query--------\n")
#It gives the insert statement based on the attributes present in the table
#This is based on PDO insert Query
print(phpgenerator.getInsertQuery())
print("\n------Generate the Execute Statement--------\n")
#This will generate the Execute Statement for the PHP
print(phpgenerator.getExecuteStatement())
print("\n------File is Generated DbConnect Template if file does not exists--------\n")
#This will generate the Database connection template
phpgenerator.createConnectionTemplateFile()

print("\n----File is Generated for INSERT Query  .php file if file does not exists-------\n")
#This will create PHP file for the given table 
phpgenerator.createPHPQueryFile()
