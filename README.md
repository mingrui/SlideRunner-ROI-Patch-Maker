Generate patches from SlideRunner annotation database

https://github.com/maubreville/SlideRunner

```
$ python make_patch.py --sqlite roi-test.sqlite --wsidir /mnt/DATA/hanli-office-test/ --pngdir png-output
```

Currently supports:
* Spot Annotation

From

<img src="readme/Selection_140.png" width="300"/>

To

1             |  2 | 3
:-------------------------:|:-------------------------:|:-------------------------:
<img src="readme/21170-26612.png" width="100"/>  | <img src="readme/21373-26539.png" width="100"/> | <img src="readme/21498-26487.png" width="100"/>
