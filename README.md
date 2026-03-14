<p align="center">
  <img src="CosmicMixer/assets/cosmic_logo.png" width="140">
</p>

<h1 align="center">Cosmic Mixer</h1>

<p align="center">
A lightweight desktop audio mixer for Linux built with PyQt6.
</p>

Cosmic Mixer provides a clean interface to control system audio streams, change default input and output devices, and adjust application volumes in real time.

The application is designed to work well in modern Linux environments such as Wayland compositors while remaining simple and responsive.

## Installation

To install the latest development version:

```bash
git clone https://github.com/elementare/CosmicMixer.git
pipx install ./CosmicMixer
```

## Running

After installation, start the mixer with:

```bash
cosmic-mixer
```

You can also run directly from the source tree:

```bash
python -m CosmicMixer.mixer
```

## Customization

Cosmic Mixer supports custom SCSS themes.

The reference theme is `cosmic.scss`, but the recommended workflow is to create a new theme based on it instead of editing it directly.

Custom themes live in:

`~/.config/cosmic-mixer/themes/`

They can be loaded with:

```bash
cosmic-mixer --theme mytheme
```

Full theme documentation is available here:

[Theme customization guide](docs/customization.md)

## License

The software is licensed under the terms of the MIT License and is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY.



