python_binary(
  name="chaps",
  source="chaps.py",
  dependencies=[
    ":lib",
    "src/python/twitter/common/app",
    "src/python/twitter/common/log",
    "3rdparty/python:sarge",
  ],
)

python_library(
  name="lib",
  sources=["lib.py"],
  dependencies=[
    "3rdparty/python:sarge",
  ],
)
