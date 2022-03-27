import akka.actor.ActorSystem
import com.newmotion.akka.rabbitmq._
import com.rabbitmq.client.BuiltinExchangeType
import com.typesafe.config._

import scala.jdk.CollectionConverters._

class ImageFinderRabbitMqSetupApp {
  import ImageFinderRabbitMqSetupApp._
  implicit val system: ActorSystem = ActorSystem("RabbitSystem")

  def start(): Unit = {
    val connection = createConnection()
    val channel = createChannel(connection)
    TOPICS.foreach(topic => createQueue(channel, topic))
    exit(channel, connection)
  }

  def createConnection(): Connection = {
    val factory = new ConnectionFactory()
    factory.setUsername(USERNAME)
    factory.setPassword(PASSWORD)
    factory.setPort(PORT)
    factory.setHost(ADDRESS)
    factory.newConnection
  }

  def createChannel(connection: Connection): Channel = {
    val channel: Channel = connection.createChannel
    channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.TOPIC)
    channel.basicQos(1)
    scribe.info(s"Channel in exchange $EXCHANGE_NAME created")
    channel
  }

  def createQueue(channel: Channel, queueName: String): Unit = {
    channel.queueDeclare(s"$QUEUE_PREFIX.$queueName", false, false, false, null)
    channel.queueBind(s"$QUEUE_PREFIX.$queueName", EXCHANGE_NAME, queueName)
    scribe.info(s"Queue $queueName created")
  }

  def exit(channel: Channel, connection: Connection): Unit = {
    scribe.info("Exiting ImageFinderRabbitMqSetupApp")
    channel.close()
    connection.close()
    System.exit(0)
  }
}

object ImageFinderRabbitMqSetupApp extends App {
  val conf = ConfigFactory.load().getConfig("ImageFinderRabbitMq")

  val ADDRESS       = conf.getString("rabbitMqAddress")
  val PORT          = conf.getString("rabbitMqPort").toInt
  val USERNAME      = conf.getString("rabbitMqUser")
  val PASSWORD      = conf.getString("rabbitMqPassword")
  val QUEUE_PREFIX  = conf.getString("topic_prefix")
  val TOPICS        = conf.getList("topics").unwrapped().asScala.map(_.toString).toList
  val EXCHANGE_NAME = "ImageFinder"

  new ImageFinderRabbitMqSetupApp().start()
}
