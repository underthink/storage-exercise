# Land Storage Assignment

## Running

You can run this application either directly from Python, using something like:

```bash
$ python3 -m src
```

..optionally passing in arguments to control the input starting balance CSVs
and movement data (see `python3 -m src --help` for more details)

Alternatively, you can run this through docker:

```bash
$ docker build --target application_image -t storage_app .
$ docker run storage_app
```

### Unit Tests

Tests can be run from the command line:

```bash
$ python3 -m unittest
```

...or from docker:

```bash
$ docker build --target test_image -t storage_app_tests .
$ docker run storage_app_tests
```

## Todo

Some other things I'd look at given more time:

* Dates and times are current naive - they should be timezone-aware
* The program doesn't currently do anything to handle likely data errors (eg
  ships claiming to offload more than the port can receive)
* More test cases for more edge cases.
* I've assumed the movement data is complete and that we won't need to
  inspect the port levels mid-way through processing a movement file. 
  This allows me to stream the movement file without sorting rows.
* pyproject config (or the like), CI/CD with linting, etc
