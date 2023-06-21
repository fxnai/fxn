# Function

[Logo strip]

Run AI prediction functions (a.k.a "predictors") in your Python apps. With Function, you can build AI-powered apps by creating and/or combining GPU-accelerated predictors that run in the cloud. In a few steps:

## Installing Function
Function is distributed on PyPi. This distribution contains both the Python and command line interface (CLI) clients. To install, open a terminal and run the following command:
```sh
pip install fxn
```

> Note that Function requires Python 3.9+

## Signing in to Function
Head over to [fxn.ai](https://fxn.ai) to create an account by logging in. Once you do, generate an access key:

[GIF here]

Now, let's login to the Function CLI with your access key. Open a terminal and run the following command:
```sh
fxn auth login <ACCESS KEY>
```

You should see information about your Function account:

[GIF here]

## Running a Predictor
You can start off by running an existing predictor [on Function](https://fxn.ai/explore):

[GIF here]

Let's run the [`@natml/stable-diffusion`](https://fxn.ai/@natml/stable-diffusion) predictor which accepts a text `prompt` and generates a corresponding image. In terminal, run the following command:

```sh
fxn predict @natml/stable-diffusion --prompt "An astronaut riding a horse on the moon"
```

And within a few seconds, you should see a creepy-looking image pop up 😅:

[GIF here]

## Creating a Predictor
At some point, you might want to create your own predictor. With Function, you don't have to deal with GitHub repos, Dockerfiles, or weird YAMLs. All you need is a Jupyter Notebook with a `predict` function. See [examples](examples/) for more.