# KalutServer
This is an implementation of a kahoot server.
To configure the server please visit the config.py file.
To run the server all you need is a computer with rsa keys and the mysql connector from oracle installed.
# Database Config
Your database must be set up as follows:
1. Create a database and specify it's name in the config file.
2. Add table quizes with columns:
   uid int(11) AI PK
   quiz json
   description json
3. Add a table users with columns:
   username varchar(45) PK
   password varchar(100)
   my_quizes json
   fav_quizes json
4. And you are done!
# Final Notes
If you have set up the database correctly, the server should work.
# JSON Stacture
1. my_quizes and fav_quizes contain a json: {"uids" : [ \<list of uids> ] }
2. quiz json stracture: [ {"Time" : question time, "Question": question string, "Answers": [ {"Key": answer, "Value": right/wrong }, ...] } }, ...]
3. description json stacture: {"UID" : uid, "Name": name of quiz, "Description" : desc of quiz, "Timeout" : player join timeout}
