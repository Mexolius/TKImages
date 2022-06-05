defmodule Receive do
  use GenServer
  use AMQP

  def init(_opts) do
    options = Application.fetch_env!(:text_server, :options)

    {:ok, connection} = AMQP.Connection.open(options)
    {:ok, channel} = AMQP.Channel.open(connection)
    AMQP.Queue.declare(channel, "image_finder.text")
    AMQP.Queue.declare(channel, "image_finder.results")

    AMQP.Basic.consume(channel, "image_finder.text")

    IO.puts(" [*] Waiting for messages. To exit press CTRL+C, CTRL+C")

    Receive.wait_for_messages(channel)
  end

  def handle_payload(payload, channel, tag) do
    body = Poison.decode!(payload)
    IO.puts(" [x] Received ")
    IO.inspect(body)
    paths = Map.get(body, "paths") || []
    options = Map.get(body, "params") || %{}

    AMQP.Basic.ack(channel, tag)

    pathsFiltered = Ocr.filterPaths(paths, options)

    response = %{
      result: 200,
      paths: pathsFiltered,
      total: length(pathsFiltered),
      sender: "text_service"
    }

    response
  end

  def wait_for_messages(channel) do
    receive do
      {:basic_deliver, payload, %{delivery_tag: tag, redelivered: _redelivered}} ->
        response = handle_payload(payload, channel, tag)
        AMQP.Basic.publish(channel, "", "image_finder.results", Poison.encode!(response))

        wait_for_messages(channel)
    end
  end
end
