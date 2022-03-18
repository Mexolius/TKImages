name := "ImageFinderRabbitMqSetupApp"

version := "0.1"

scalaVersion := "2.13.8"

libraryDependencies += "com.outr" %% "scribe" % "3.8.0"
libraryDependencies += "com.newmotion" %% "akka-rabbitmq" % "6.0.0"
libraryDependencies += "com.typesafe" % "config" % "1.4.2"
// https://mvnrepository.com/artifact/com.typesafe.akka/akka-actor
libraryDependencies += "com.typesafe.akka" %% "akka-actor" % "2.6.18"
