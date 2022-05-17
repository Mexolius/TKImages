defmodule TextServer.MixProject do
  use Mix.Project

  def project do
    [
      app: :text_server,
      version: "0.1.0",
      elixir: "~> 1.13",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [applications: [:amqp]]

    [
      extra_applications: [:poison,:logger,:tesseract_ocr]
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:tesseract_ocr, "~> 0.1.5"},
      {:amqp, "~> 1.0"},
      {:poison, "~> 3.1"},
    ]
  end
end
