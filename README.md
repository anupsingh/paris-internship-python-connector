Project requirements
=======

Your workstation must have the following elements installed:

 - Java Development Kit 8 - JDK 8 - in its latest version.
 - Maven 3

Start the server
==========

To start the server:

 1. go into the directory _server_.  
 2. Then, first compile the project using `mvn install`.
 3. Finally, run `mvn exec:java@serve`. This will launch the server onto port 9090. You can go to http://localhost:9090 to browse the data. Use user _admin_ with password _admin_ to connect.

Alternatively, you can import the Maven project stored in _server/_ into any Java IDE - Eclipse, Intellij, Netbeans - and launch the class `PyPivotServer`.

**Warning**: To run this project, you need a license for ActivePivot.