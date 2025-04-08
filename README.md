# Function for Python

![function logo](https://raw.githubusercontent.com/fxnai/.github/main/logo_wide.png)

[![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fdiscord.com%2Fapi%2Finvites%2Fy5vwgXkz2f%3Fwith_counts%3Dtrue&query=%24.approximate_member_count&logo=discord&logoColor=white&label=Function%20community)](https://discord.gg/fxn)

Run prediction functions (a.k.a "predictors") locally in your Python apps, with full GPU acceleration and zero dependencies.

> [!TIP]
> [Join our waitlist](https://fxn.ai/waitlist) to bring your custom Python functions and run them on-device across Android, iOS, macOS, Linux, web, and Windows.

## Installing Function
Function is distributed on PyPi. This distribution contains both the Python client and the command line interface (CLI). To install, open a terminal and run the following command:
```sh
# Install Function
$ pip install --upgrade fxn
```

> [!NOTE]
> Function requires Python 3.10+

## Retrieving your Access Key
Head over to [fxn.ai](https://www.fxn.ai/account/developer) to create an account by logging in. Once you do, generate an access key:

![generate access key](https://raw.githubusercontent.com/fxnai/.github/main/access_key.gif)

## Making a Prediction
First, create a Function client, specifying your access key:
```py
from fxn import Function

# Create the Function client
fxn = Function(access_key="<Function access key>")
```

Then make a prediction:
```py
# Create a prediction
prediction = fxn.predictions.create(
    tag="@fxn/greeting",
    inputs={ "name": "Peter" }
)
# Print the returned greeting
print(prediction.results[0])
```

## Using the Function CLI
Open up a terminal and login to the Function CLI:
```sh
# Login to Function
$ fxn auth login <ACCESS KEY>
```

Then make a prediction:
```sh
# Make a prediction using the Function CLI
$ fxn predict @fxn/greeting --name Peter
```

___

## Useful Links
- [Discover predictors to use in your apps](https://fxn.ai/explore).
- [Join our Discord community](https://discord.gg/fxn).
- [Check out our docs](https://docs.fxn.ai).
- Learn more about us [on our blog](https://blog.fxn.ai).
- Reach out to us at [hi@fxn.ai](mailto:hi@fxn.ai).

Function is a product of [NatML Inc](https://github.com/natmlx).
