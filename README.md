# JOIN ME TO THE MOON!
![alt text](assets/moon.jpg)


# How to Use
Bot is driven by file `main.py`

Currently I have not set up command line arguments, so you need to edit the file in `main.py` to change your base coin and trade coins.

For example, 
```python
Bot(base_coin='BTC', symbols=['PHX', 'BAT'])
```

Add a python file to the directory named `config.py` structured like the following:

```python
api_key = "xxx"
api_secret = "xxx"
```

Then run `python3 main.py`. If you wish to run the bot as a background task you can use the `run.sh` file.
```
chmod u+x run.sh
./run.sh
```
This is how I run the bot on AWS EC2 instance.
