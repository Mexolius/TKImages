defmodule ReceiveTest do
  use ExUnit.Case

  @rootDir File.cwd!()

  @data %{
    "params" => %{},
    "paths" => [
      "#{@rootDir}/test/resources/not_text.png",
      "#{@rootDir}/test/resources/not_text.png",
      "#{@rootDir}/test/resources/text.png",
      "#{@rootDir}/test/resources/text.png",
      "#{@rootDir}/test/resources/pattern_text.png",
      "#{@rootDir}/test/resources/pattern_text.png",
      "#{@rootDir}/test/resources/nofile.png"
    ]
  }

  def testRequest(testData, expected) do
    paths = Map.get(testData, "paths") || []
    options = Map.get(testData, "params") || %{}
    pathsFiltered = Ocr.filterPaths(paths, options)

    assert Enum.sort(expected) == Enum.sort(pathsFiltered)
  end

  test "has text" do
    testData = Map.put(@data, "params", %{"hasText" => "true"})

    expected = [
      "#{@rootDir}/test/resources/text.png",
      "#{@rootDir}/test/resources/text.png",
      "#{@rootDir}/test/resources/pattern_text.png",
      "#{@rootDir}/test/resources/pattern_text.png"
    ]

    testRequest(testData, expected)
  end

  test "has no text" do
    testData = Map.put(@data, "params", %{"hasText" => "false"})

    expected = [
      "#{@rootDir}/test/resources/not_text.png",
      "#{@rootDir}/test/resources/not_text.png",
      "#{@rootDir}/test/resources/nofile.png"
    ]

    testRequest(testData, expected)
  end

  test "contains text ''" do
    testData = Map.put(@data, "params", %{"containsText" => ""})

    expected = @data["paths"]

    testRequest(testData, expected)
  end

  test "contains text 'this'" do
    testData = Map.put(@data, "params", %{"containsText" => "this"})

    expected = [
      "#{@rootDir}/test/resources/text.png",
      "#{@rootDir}/test/resources/text.png"
    ]

    testRequest(testData, expected)
  end

  test "minLength 100" do
    testData = Map.put(@data, "params", %{"minLength" => "100"})

    expected = [
      "#{@rootDir}/test/resources/text.png",
      "#{@rootDir}/test/resources/text.png"
    ]

    testRequest(testData, expected)
  end

  test "maxLength 100" do
    testData = Map.put(@data, "params", %{"maxLength" => "100"})

    expected = [
      "#{@rootDir}/test/resources/not_text.png",
      "#{@rootDir}/test/resources/not_text.png",
      "#{@rootDir}/test/resources/pattern_text.png",
      "#{@rootDir}/test/resources/pattern_text.png",
      "#{@rootDir}/test/resources/nofile.png"
    ]

    testRequest(testData, expected)
  end

  test "maxLength 100 and has text" do
    testData = Map.put(@data, "params", %{"hasText" => "true", "maxLength" => "100"})

    expected = [
      "#{@rootDir}/test/resources/pattern_text.png",
      "#{@rootDir}/test/resources/pattern_text.png"
    ]

    testRequest(testData, expected)
  end
end
