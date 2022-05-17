defmodule TextServerTest do
  use ExUnit.Case
  doctest TextServer

  test "greets the world" do
    assert TextServer.hello() == :world
  end
end
