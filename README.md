# eCognition-block-template
![coverage](coverage.svg)

This repository serves as a template for building an eCognition-powered block
for UP42 platform. 

UP42 platform provides a host of data and algorithms from different sources.
Developing the eCognition-powered block, you would be able to integrate your
algorithm with those data sources and algorithms and also publish your own block
on the UP42 marketplace.

The block uses the [eCognition command line
engine](https://hub.docker.com/r/ecognition/linux_cle) and requires `eCognition
ruleset`. The ruleset needs to be created with your eCognition application and
license. Please have a look at some official eCognition [rule set
examples][ruleset-examples] and [documentation][ecognition-doc].

## Who is this repository for?
The repository is made for a UP42 Partner who intends to build an
eCognition-powered application block. The partner with eCognition developer
license should be able to create an `eCognition ruleset` & has knowledge of
`python`

## How to build your custom eCognition-powered block?

Steps to build & upload your eCognition-powered block to UP42:

- [ ] Add Ruleset
  
  Place your eCognition ruleset in the `/ruleset` folder and adjust the [RULESET_PATH][repo-manifest-ruleset-config] if required. 
  

- [ ] Configure Block

  Configure `UP42Mainfest.json` and `marketplace.json`, see the [UP42 custom
  block documentation][up42-custom-block-doc]. 

  **The configuration should answer the following key questions:**
  - Is the [name][repo-manifest-block-name] of the block set correctly?
  - Is [machine type][repo-manifest-machine-types] set correctly as per [documentation][machine-types]?
  - Are [input capabilities][repo-manifest-input-capabilities] & [output capabilities][repo-manifest-output-capabilities] configured correctly as suggested [block capabilities documentation][block-capabilities]? *The input & output capabilities define the compatibility of your block with any other upstream & downstream blocks.*
  - Are all [user parameters][repo-manifest-parameters] added in the manifest in compliance with the [parameter schema][runtime-parameters]? *The parameter name has one-to-one mapping with the eCognition ruleset in the current template. Therefore, only adjusting `UP42Manifest.json` is sufficient. These parameters will then appear at the block parameter configuration step when configuring a workflow on UP42.*

- [ ] Make sure to adjust [actual code][repo-process-block] if input & output data manipulations are required. For example, if your process outputs a vector file in a different location than one in the code, make sure that you've adjusted that.

- [ ] Build custom block container

  ```shell
  >> make build
  ``` 
- [ ] Upload the block to UP42 by following these [instructions][up42-first-custom-block]

## How to test your block?

### Testing block locally

- Prepare environment & test

  ```shell
  # Install runtime environments
  >> pip install -r requirements.txt
  
  # Install development environments
  >> pip install -r requirements-dev.txt

  # Run block tests
  >> make test

  ```

### Testing block on production
- Make sure you've created a custom block with the
[instructions](#how-to-build-your-custom-ecognition-block) and pushed your block
to the UP42 platform.

- Please contact UP42 to whitelist your custom block for `eCognition License Server` access
- After your custom block is whitelisted, you should [create][create-workflow] workflows, [configure][configure-job] & [run][run-job] jobs using the console to test your block on the UP42 platform or [test using SDK][sdk-workflow-and-job].




<!-- All link references -->
[up42-first-custom-block]: https://docs.up42.com/getting-started/first-custom-block.html
[up42-custom-block-doc]: https://docs.up42.com/going-further/custom-processing-block-dev.html
[ecognition-doc]: https://support.ecognition.com/hc/en-us/categories/360002401060-Library-
[machine-types]: https://docs.up42.com/account/credits#machine-type
[block-capabilities]: https://docs.up42.com/processing-platform/custom-blocks/capabilities
[ruleset-examples]: https://support.ecognition.com/hc/en-us/sections/360004538160-Project-Rule-Set-Examples
[create-workflow]: https://docs.up42.com/processing-platform/workflows/create-workflow-commercial
[configure-job]: https://docs.up42.com/processing-platform/jobs/configure-job-commercial
[run-job]: https://docs.up42.com/processing-platform/jobs/run-job-commercial
[sdk-workflow-and-job]: https://sdk.up42.com/analytics_workflow/ 
[runtime-parameters]: https://docs.up42.com/processing-platform/custom-blocks/parameters#processing-parameters

<!--- All Repository Parmalinks --->
[repo-manifest-block-name]: https://github.com/up42/ecognition-powered-block-template/blob/master/UP42Manifest.json#L3
[repo-manifest-machine-types]: https://github.com/up42/ecognition-powered-block-template/blob/master/UP42Manifest.json#L13-L15
[repo-manifest-output-capabilities]: https://github.com/up42/ecognition-powered-block-template/blob/master/UP42Manifest.json#L28-L39
[repo-manifest-ruleset-config]: https://github.com/up42/ecognition-powered-block-template/blob/master/src/config.py#L11
[repo-manifest-input-capabilities]: https://github.com/up42/ecognition-powered-block-template/blob/master/UP42Manifest.json#L16-L27
[repo-process-block]: https://github.com/up42/ecognition-powered-block-template/blob/master/src/ecognition.py#L164-L191
[repo-manifest-parameters]: https://github.com/up42/ecognition-powered-block-template/blob/master/UP42Manifest.json#L12
