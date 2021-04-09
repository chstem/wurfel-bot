# Telegram Würfel Bot

A Python Telegram Bot to create sentences by randomly choosing from a list of provided text snippets. You may use it to build things like random name generators.

## Configuration

Set the environment variables `WURFEL_TG_TOKEN` with your Telegram bot token and `WURFEL_FILES` with the path to your custom YAML file.

The YAML file inlcudes some basic configuration and the text snippets to build a randomly generated sentence. See `dices.yaml` for a very basic example and `pets.yaml` a slightly more complex one.

 - `triggers`: If privacy mode is enabled, the bot will react to messages containing any of the keywords in this list.
 - `markdown`: A boolean to enable markdown support.
 - `separator`: The string used to separate the parts of the sentence.
 - `dices`: A nested list of strings. From each inner list one option is randomly chosen. Instead of a string, a key-value map may be used. The key is used as an annotation for the string. String with same annotation will be matched together in the final output to allow for proper grammar.

In addition to the trigger keywords, a bot command is created following the basename of the used YAML file, i.e. `/dices` and `/pets` for the provided examples.

### Proper grammar with key-value mapping

Each key needs to have one occurence where it is the only option. In case of the `pets.yaml` example this is the number of pets:

```
  - - 1: _only_
    - 2: "*two*"
    - 3: "*three*"
```

Options including multiple key-value pairs will be selected accordingly

```
  - - 1: dog 🐶
      2: dogs 🐶🐶
      3: dogs 🐶🐶🐶
    - 1: cat 😸
      2: cats 😸😸
      3: cats 😸😸😸
```

This may result in `_only_ dog` or `*two* cats 😸😸`, while things like `*three* cat 😸` are not possible.

Similar, the randomly chosen name (Alice or Bob) will select the appropriate pronoun (her or his).