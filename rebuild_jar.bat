cd reference\BFSPMiner-java\BFSPMiner
mkdir target\classes_new
javac -d target\classes_new src\main\java\utils\*.java src\main\java\model\*.java src\main\java\algorithm\*.java
jar cvf target\BFSPMiner-1.0.0.jar -C target\classes_new .
