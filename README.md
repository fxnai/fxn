# Function for Python and CLI

![function logo](https://raw.githubusercontent.com/fxnai/.github/main/logo_wide.png)

Run AI prediction functions (a.k.a "predictors") in your Python apps. With Function, you can build AI-powered apps by creating and composing GPU-accelerated predictors that run in the cloud. In a few steps:

## Installing Function
Function is distributed on PyPi. This distribution contains both the Python client and the command line interface (CLI). To install, open a terminal and run the following command:
```sh
pip install fxn
```

> Note that Function requires Python 3.9+

## Signing in to Function
Head over to [fxn.ai](https://fxn.ai) to create an account by logging in. Once you do, generate an access key:

![generate access key](https://raw.githubusercontent.com/fxnai/.github/main/access_key.gif)

Now, let's login to the Function CLI with your access key. Open a terminal and run the following command:
```sh
fxn auth login <ACCESS KEY>
```

You should see information about your Function account:

![login to CLI](https://raw.githubusercontent.com/fxnai/.github/main/auth_login.gif)

## Making a Prediction
You can start off by running an existing predictor [on Function](https://fxn.ai/explore). Let's run the [`@natml/stable-diffusion`](https://fxn.ai/@natml/stable-diffusion) predictor which accepts a text `prompt` and generates a corresponding image. In terminal, run the following command:

```sh
fxn predict @natml/stable-diffusion --prompt "An astronaut riding a horse on the moon"
```

And within a few seconds, you should see a creepy-looking image pop up 😅:

![prediction](https://raw.githubusercontent.com/fxnai/.github/main/predict.gif)

## Creating a Predictor
At some point, you might want to create your own predictor. With Function, you don't have to deal with GitHub repos, Dockerfiles, or weird YAMLs. All you need is a Jupyter Notebook with a `predict` function. See our [samples project](https://github.com/fxnai/samples) for more.

___

## Useful Links
- [Discover predictors to use in your apps](https://fxn.ai/explore).
- [Join our Discord community](https://fxn.ai/community).
- [Check out our docs](https://docs.fxn.ai).
- Learn more about us [on our blog](https://blog.fxn.ai).
- Reach out to us at [hi@fxn.ai](mailto:hi@fxn.ai).

Function is a product of [NatML Inc](https://github.com/natmlx).