
# Theme Customization

Cosmic Mixer supports custom SCSS themes.

Themes are composed of two parts:

- **base.scss** – defines the UI structure and styling rules
- **palettes** – define the color scheme applied to the base theme

The default packaged theme should be treated as the reference implementation.

Custom themes are loaded from:

`~/.config/cosmic-mixer/themes/`

When Cosmic Mixer runs for the first time, it creates the following structure:

```
~/.config/cosmic-mixer/themes/base.scss
~/.config/cosmic-mixer/themes/palettes/cosmic.scss
```

Palette files are automatically compiled when the application starts.

---

# Recommended Workflow

Create a new palette based on the reference theme.

```bash
cp ~/.config/cosmic-mixer/themes/palettes/cosmic.scss \
   ~/.config/cosmic-mixer/themes/palettes/mytheme.scss
```

Edit the new palette:

```bash
vim ~/.config/cosmic-mixer/themes/palettes/mytheme.scss
```

Then launch Cosmic Mixer with:

```bash
cosmic-mixer --theme mytheme
```

The application will compile:

```
~/.config/cosmic-mixer/themes/palettes/mytheme.scss
```

into:

```
~/.config/cosmic-mixer/themes/mytheme.css
```

and apply it automatically.

---

# Resetting the Reference Theme

If you want to restore the default packaged themes, run:

```bash
cosmic-mixer --reset-theme
```

This restores:

```
~/.config/cosmic-mixer/themes/base.scss
~/.config/cosmic-mixer/themes/palettes/cosmic.scss
```

to their packaged versions.

---

# Theme Structure

Themes work by defining color variables in a palette file and then importing the base theme.

Example palette:

```scss
$background: #0f021e;
$surface: #140628;
$surface-alt: #0d051a;

$border: #4a2180;

$primary: #ff5277;
$secondary: #ff9d00;

$text: #e0d8f0;
$text-muted: #a48bbd;

$foreground-strong: #ffffff;

@import "../base";
```

The palette defines the color variables and then imports `base.scss`, which applies those variables to the interface.

---

# Theme Variables

The default palette defines these base color variables:

```scss
$background
$surface
$surface-alt
$border
$primary
$secondary
$text
$text-muted
$foreground-strong
```

### Variable meanings

* `$background`
  Main application background.

* `$surface`
  Panel background color.

* `$surface-alt`
  Background used for inputs, selectors, slider grooves, and scrollbars.

* `$border`
  Border and separator color across the interface.

* `$primary`
  Main highlight color, used for titles, slider fill, and focused elements.

* `$secondary`
  Secondary highlight color, used for application headers and slider hover states.

* `$text`
  Main text color.

* `$text-muted`
  Softer text color for stream labels, placeholders, and secondary elements.

* `$foreground-strong`
  Strong contrast color used for slider handles and selected text.

---

# Advanced Customization

While palettes change the **color scheme**, it is also possible to completely redesign the UI.

By editing:

```
~/.config/cosmic-mixer/themes/base.scss
```

you can modify the entire interface:

* layout styling
* widget appearance
* sliders
* scrollbars
* typography
* borders and spacing

This allows the program to be **fully reskinned**, not just recolored.

All palettes will automatically inherit any structural changes made in `base.scss`.

---

# Main Selectors

These are the main selectors used by the default theme.

### Main window

```scss
#MainWin
```

Controls the main mixer window.

### Logo

```scss
QLabel#LogoLabel
```

Controls spacing and appearance of the logo.

### Main title

```scss
QLabel[class="MasterTitle"]
```

Controls the main title text.

### Section labels

```scss
QLabel[class="SectionLabel"]
```

Used for labels such as `GLOBAL OUTPUT` and `GLOBAL INPUT`.

### Application headers

```scss
QLabel[class="AppHeader"]
```

Used for the header of each application group.

### Stream labels

```scss
QLabel[class="StreamTitle"]
```

Used for individual stream names.

### Mute icon

```scss
QLabel[class="MuteIcon"]
```

Controls the mute icon appearance.

### Search bar

```scss
QLineEdit#SearchBar
```

Controls the stream search field.

### Device selectors

```scss
QComboBox
QComboBox#GlobalOutput
QComboBox#GlobalInput
QComboBox#StreamOutputSelector
```

Controls the appearance of device dropdowns.

### Scroll area

```scss
QScrollArea
QScrollArea#MixerScrollArea
QWidget#ScrollContent
```

Controls the scrolling region for stream rows.

### Scrollbar

```scss
QScrollBar:vertical
QScrollBar::handle:vertical
```

Controls the vertical scrollbar.

### Slider row container

```scss
QWidget[class="SliderRow"]
```

Used for each stream row container.

### Volume slider

```scss
QSlider#VolumeSlider
QSlider#VolumeSlider::groove:horizontal
QSlider#VolumeSlider::sub-page:horizontal
QSlider#VolumeSlider::add-page:horizontal
QSlider#VolumeSlider::handle:horizontal
```

Controls the volume slider appearance.

### Header separator

```scss
#HeaderSeparator
```

Controls the thin separator below the header.

---

# Notes

* Theme names are passed without extension.
  Example: `--theme mytheme` loads `mytheme.scss` and `mytheme.css`.

* `.scss` files are the editable source files.
  `.css` files are generated automatically.

* If a theme is broken, the application may fail to apply some rules. In that case, compare your theme with the reference `cosmic.scss`.

* The safest way to start a new theme is to copy the reference palette and modify it incrementally.


