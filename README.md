# Fan Tray Icon

## Prerequisite

* python==3.10
* virtualenv

## Running

```python
(venv) fan@fanPC:~/utils/fan_tray_icon$ python main.py
```

## Command for Gnome Startup App

```shell
bash --login -c 'cd $HOME/utils/fan_tray_icon && source venv/bin/activate && python main.py;disown -r;exit 0'
```