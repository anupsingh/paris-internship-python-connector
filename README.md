# Project requirements

Your workstation must have the following elements installed:

- Java Development Kit 8 - [JDK 8 - in its latest version](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html).
- [Maven 3](https://maven.apache.org/download.cgi)
- Python 3
- [pipenv](https://pipenv.readthedocs.io/en/latest/#install-pipenv-today)

# Start the server

To start the server:

1.  go into the directory _server_.
2.  you have to download the _license_ and then define its location in an environment variable `ACTIVEPIVOT_LICENSE`
3.  Then, first compile the project using `mvn install`.
4.  Finally, run `mvn exec:java@serve`. This will launch the server onto port 9090. You can go to http://localhost:9090 to browse the data. Use user _admin_ with password _admin_ to connect (if you're using macOS, run `mvn exec:java@serve -DchunkAllocatorClass=com.qfs.chunk.direct.impl.MmapDirectChunkAllocator`).

Alternatively, you can import the Maven project stored in _server/_ into any Java IDE - Eclipse, Intellij, Netbeans - and launch the class `PyPivotServer`.

**Warning**: To run this project, you need a license for ActivePivot.

# Start the python connector

To start the connector:

1. go into the directory _python_
2. Then, run `pipenv install`

## Commands

- To have access to the venv's shell: `pipenv shell` (and then `deactivate` to go out of it)
- To have access to a python shell: `pipenv run python`
