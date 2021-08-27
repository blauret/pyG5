# PyG5

## Description

This project aims at development a Garmin G5 view targeting a Raspberry Pi
display (640x480) in vertical. The intent it to provide a G5 Attitude indicator + G5 Horizontal Situation Indicator stacked on the display in vertical mode. The G5 connects to X-Plane flight simulator

It does not require plugin and use the standard DREF UDP interface from X-Plane. It should not require any configuration. Start it and
it will connect to X-Plane and fetch the required data.

![demoView](assets/demoView.png)

## Maturity

It's currently in pretty early phase. It's functional and should be easy to install but might suffer from issues here and  there.

## Installation

```console
        > sudo pip install pyG5
```

## Running

```console
        > pyG5
```

## Developer
mk


## License

[License files](LICENSE.TXT)
