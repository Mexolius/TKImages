defmodule Ocr do
  def pass(_outputOcr) do
    true
  end

  def hasText(flag, outputOcr) do
    has = String.length(outputOcr) > 0

    if flag == "true" do
      has
    else
      not has
    end
  end

  def containsText(text, outputOcr) do
    String.contains?(outputOcr, text)
  end

  def compareLength(operator, number, outputOcr) do
    case Integer.parse(number) do
      {intVal, ""} ->
        operator.(String.length(outputOcr), intVal)

      :error ->
        IO.puts("Is not a number #{number}")
        &pass/1
    end
  end

  def minLength(number, outputOcr) do
    compareLength(&Kernel.>=/2, number, outputOcr)
  end

  def maxLength(number, outputOcr) do
    compareLength(&Kernel.<=/2, number, outputOcr)
  end

  def parseOption(option) do
    {name, param} = option

    case String.trim(name) do
      "hasText" ->
        &hasText(param, &1)

      "containsText" ->
        &containsText(String.downcase(param), String.downcase(&1))

      "minLength" ->
        &minLength(param, &1)

      "maxLength" ->
        &maxLength(param, &1)

      "name" ->
        &pass/1

      _ ->
        IO.warn("Unknown function name #{name}")
        &pass/1
    end
  end

  def checkImage(path, options) do
    outputOcr = TesseractOcr.read(path)
    checked = Enum.map(options, fn option -> parseOption(option).(outputOcr) end)
    Enum.all?(checked)
  end

  def filterPaths(paths, options) do
    paths
    |> Enum.map(fn path ->
      Task.async(fn ->
        [path, Ocr.checkImage(path, options)]
      end)
    end)
    |> Enum.map(fn tsk -> Task.await(tsk) end)
    |> Enum.filter(fn tsk -> Enum.at(tsk, 1) end)
    |> Enum.map(fn tsk -> Enum.at(tsk, 0) end)
  end
end
