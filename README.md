# Function for Python and CLI

![function logo](https://raw.githubusercontent.com/fxnai/.github/main/logo_wide.png)

[![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fdiscord.com%2Fapi%2Finvites%2Fy5vwgXkz2f%3Fwith_counts%3Dtrue&query=%24.approximate_member_count&logo=discord&logoColor=white&label=Function%20community)](https://fxn.ai/community)

Run prediction functions (a.k.a "predictors") locally in your Python apps, with full GPU acceleration and zero dependencies. In a few steps:

## Installing Function
Function is distributed on PyPi. This distribution contains both the Python client and the command line interface (CLI). To install, open a terminal and run the following command:
```sh
# Install Function
$ pip install --upgrade fxn
```

> [!NOTE]
> Function requires Python 3.9+

## Retrieving your Access Key
Head over to [fxn.ai](https://fxn.ai) to create an account by logging in. Once you do, generate an access key:

![generate access key](https://raw.githubusercontent.com/fxnai/.github/main/access_key.gif)

## Making a Prediction
Let's run the [`@fxn/greeting`](https://fxn.ai/@fxn/greeting) predictor which accepts a `name` and returns a congenial greeting. Run the following Python script:
```py
from fxn import Function

# Create the Function client
fxn = Function(access_key="<Function access key>")
# Create a prediction
prediction = fxn.predictions.create(
    tag="@fxn/greeting",
    inputs={ "name": "Peter" }
)
# Print the returned greeting
print(prediction.results[0])
```

> [!TIP]
> Explore public predictors [on Function](https://fxn.ai/explore) or [create your own](https://fxn.ai/waitlist).
r
## Using the Function CLI
Open up a terminal and run the following command:

```sh
# Login to Function
fxn auth login <ACCESS KEY>

# Make a prediction using the Function CLI
fxn predict @fxn/greeting --name Peter
```

___

## Useful Links
- [Discover predictors to use in your apps](https://fxn.ai/explore).
- [Join our Discord community](https://fxn.ai/community).
- [Check out our docs](https://docs.fxn.ai).
- Learn more about us [on our blog](https://blog.fxn.ai).
- Reach out to us at [hi@fxn.ai](mailto:hi@fxn.ai).

Function is a product of [NatML Inc](https://github.com/natmlx).
