## 0.0.9
+ Added `EnvironmentVariable` class for managing predictor environment variables.
+ Added `fxn envs` CLI command for managing predictor environment variables.

## 0.0.8
+ Fixed `fxn predictors create` CLI command raising authentication error.

## 0.0.7
+ Fixed `fxn predictors create` CLI command raising error.

## 0.0.6
+ Fixed `fxn predictors create` CLI command raising error.

## 0.0.5
+ Added `Prediction` class for making predictions.
+ Added `fxn predict` CLI command for makong predictions.
+ Updated `Predictor.create` method `type` argument to be optional. Cloud predictors are now the default.

## 0.0.4
+ Added `Predictor.create` class method for creating predictors.
+ Added `fxn predictors create` CLI command for creating predictors.
+ Fixed `User.retrieve` method raising exception when retrieving current user.
+ Fixed `fxn auth logout` CLI command erroring when user was already logged out.

## 0.0.3
+ Added `Signature` type for inspecting predictor signatures.
+ Added `Parameter` type for inspecting predictor signature parameters.
+ Added `Acceleration` enumeration for specifying predictor acceleration.
+ Added `PredictorType` enumeration for specifying predictor type.

## 0.0.2
+ Added Function API types and services.
+ Added command line interface. Run `fxn` in your terminal.

## 0.0.1
+ First pre-release.