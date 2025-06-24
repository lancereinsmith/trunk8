# Themes Configuration (config/themes.toml)

The `config/themes.toml` file contains all available themes for Trunk8's user interface and markdown rendering.

## File Purpose

This file is **read-only** and provides:

- Available theme definitions
- Theme display names
- Theme descriptions
- Theme metadata

**Note**: This file is not meant to be edited. It's automatically provided and updated with Trunk8.

## File Structure

```toml
[themes.themename]
name = "Display Name"
description = "Theme description"
```

## Available Themes

The complete list of themes with descriptions:

```toml
[themes.brite]
name = "Brite"
description = "Clean and bright design"

[themes.cerulean]
name = "Cerulean"
description = "A calm blue sky"

[themes.cosmo]
name = "Cosmo"
description = "An ode to Metro"

[themes.cyborg]
name = "Cyborg"
description = "Jet black and electric blue"

[themes.darkly]
name = "Darkly"
description = "Flatly in night mode"

[themes.flatly]
name = "Flatly"
description = "Flat and modern"

[themes.journal]
name = "Journal"
description = "Crisp like a new sheet of paper"

[themes.litera]
name = "Litera"
description = "The medium is the message"

[themes.lumen]
name = "Lumen"
description = "Light and shadow"

[themes.lux]
name = "Lux"
description = "A touch of class"

[themes.materia]
name = "Materia"
description = "Material is the metaphor"

[themes.minty]
name = "Minty"
description = "A fresh feel"

[themes.morph]
name = "Morph"
description = "A modern take"

[themes.pulse]
name = "Pulse"
description = "A trace of purple"

[themes.quartz]
name = "Quartz"
description = "A gem of a theme"

[themes.sandstone]
name = "Sandstone"
description = "A touch of warmth"

[themes.simplex]
name = "Simplex"
description = "Mini and minimalist"

[themes.sketchy]
name = "Sketchy"
description = "A hand-drawn look"

[themes.slate]
name = "Slate"
description = "Shades of gunmetal gray"

[themes.solar]
name = "Solar"
description = "A spin on Solarized"

[themes.spacelab]
name = "Spacelab"
description = "Silvery and sleek"

[themes.superhero]
name = "Superhero"
description = "The brave and the blue"

[themes.united]
name = "United"
description = "Ubuntu orange and unique font"

[themes.vapor]
name = "Vapor"
description = "A subtle theme"

[themes.yeti]
name = "Yeti"
description = "A friendly foundation"

[themes.zephyr]
name = "Zephyr"
description = "Breezy and beautiful"
```

## Theme Categories

### Light Themes

Best for daytime use and readability:

- **Flatly** - Clean, minimal
- **Lumen** - Subtle shadows
- **Litera** - Typography-focused
- **Simplex** - Ultra-minimal
- **Journal** - Paper-like
- **Minty** - Fresh green accents
- **Yeti** - Friendly blue

### Dark Themes

Perfect for low-light environments:

- **Darkly** - Flat dark design
- **Cyborg** - High contrast dark
- **Slate** - Professional gray
- **Solar** - Solarized dark variant
- **Superhero** - Dark with blue accents

### Unique Themes

Distinctive styling options:

- **Sketchy** - Hand-drawn appearance
- **Vapor** - Vaporwave aesthetic
- **Pulse** - Purple accents
- **Morph** - Modern gradients
- **Materia** - Material Design

### Professional Themes

For business environments:

- **Cosmo** - Metro-inspired
- **Lux** - Premium feel
- **United** - Ubuntu-style
- **Cerulean** - Calm blue
- **Sandstone** - Warm neutral

## Using Themes

### Setting UI Theme

In `config/config.toml`:
```toml
[app]
theme = "darkly"  # Use theme key from config/themes.toml
```

### Setting Markdown Theme

In `config/config.toml`:
```toml
[app]
markdown_theme = "flatly"  # Can be different from UI theme
```

### Via Settings Page

1. Navigate to Settings
2. Select from dropdown menus
3. Save changes

## Theme Selection Guide

### By Use Case

| Use Case | Recommended Themes |
|----------|-------------------|
| Documentation | Litera, Journal, Flatly |
| Developer Tools | Solar, Darkly, Cyborg |
| Corporate | Cosmo, Lux, United |
| Creative | Sketchy, Vapor, Pulse |
| Minimal | Simplex, Flatly, Lumen |

### By Time of Day

| Time | UI Theme | Markdown Theme |
|------|----------|----------------|
| Day | Flatly | Flatly |
| Evening | Lumen | Litera |
| Night | Darkly | Flatly |
| Late Night | Cyborg | Solar |

### By Profession

| Profession | Suggested Theme |
|------------|----------------|
| Developer | Solar, Darkly |
| Designer | Sketchy, Vapor |
| Writer | Journal, Litera |
| Business | Cosmo, Lux |
| Educator | Yeti, Cerulean |

## Theme Properties

### Visual Characteristics

Each theme affects:

- Navigation bar color
- Button styles
- Form appearance
- Table styling
- Alert colors
- Typography
- Link colors
- Background colors

### Accessibility

High contrast themes:

- **Cyborg** - Maximum contrast
- **Darkly** - Good dark contrast
- **Flatly** - Clean light contrast
- **Superhero** - Strong color contrast

### Performance

All themes have similar performance, but consider:

- Dark themes may save battery on OLED screens
- Simple themes (Simplex, Flatly) render fastest
- Complex themes (Sketchy) have more CSS

## Programmatic Access

### List Available Themes

```python
import toml

# Load themes
with open('config/themes.toml', 'r') as f:
    themes = toml.load(f)['themes']

# List all theme keys
theme_keys = list(themes.keys())
print(f"Available themes: {', '.join(theme_keys)}")

# Get theme details
for key, data in themes.items():
    print(f"{key}: {data['name']} - {data['description']}")
```

### Validate Theme Selection

```python
import toml

def is_valid_theme(theme_name):
    with open('config/themes.toml', 'r') as f:
        themes = toml.load(f)['themes']
    return theme_name in themes

# Usage
if is_valid_theme('darkly'):
    print("Valid theme!")
```

### Theme Information

```python
import toml

def get_theme_info(theme_name):
    with open('config/themes.toml', 'r') as f:
        themes = toml.load(f)['themes']
    
    if theme_name in themes:
        return themes[theme_name]
    return None

# Get theme details
info = get_theme_info('cosmo')
if info:
    print(f"Name: {info['name']}")
    print(f"Description: {info['description']}")
```

## Fallback Behavior

If `config/themes.toml` is missing or corrupted:

1. Trunk8 uses built-in fallback themes:
    - Cosmo
    - Cerulean

2. Limited theme selection available

3. Warning logged to console

## CDN Integration

Themes are loaded from Bootswatch CDN:

```html
https://cdn.jsdelivr.net/npm/bootswatch@5/dist/{theme}/bootstrap.min.css
```

Benefits:

- Fast global delivery
- Automatic updates
- Reduced server load
- Browser caching


## Theme Development

### Understanding Bootswatch

All themes are from [Bootswatch](https://bootswatch.com/):

- Built on Bootstrap 5
- Consistent structure
- Professional design
- Open source (MIT)

### Theme Variables

Each theme modifies Bootstrap variables:

- `$primary`: Main brand color
- `$secondary`: Secondary color
- `$success`: Success state color
- `$danger`: Error state color
- `$warning`: Warning state color
- `$info`: Information color
- `$light`: Light background
- `$dark`: Dark elements

## Troubleshooting

### Theme Not Found

If a theme isn't working:

1. Check spelling (case-sensitive)
2. Verify theme exists in `config/themes.toml`
3. Clear browser cache
4. Check CDN accessibility

### Inconsistent Appearance

- Some themes work better for certain content
- Test both UI and markdown rendering
- Consider user preferences
- Check browser compatibility

### Performance Issues

- CDN may be blocked in some regions
- Consider local hosting for critical apps
- Browser extensions may interfere
- Clear cache if themes look broken

## Best Practices

### Theme Selection

1. **Consider your audience**
    - Professional vs casual
    - Accessibility needs
    - Cultural preferences

2. **Test thoroughly**
    - All page types
    - Different devices
    - Various browsers

3. **Be consistent**
    - Document theme choices
    - Consider brand guidelines
    - Plan for future changes

### Maintenance

- Themes auto-update via CDN
- No manual updates needed
- Monitor for visual breaks
- Test after Bootstrap updates

## Next Steps

- Configure themes in [Application Config](app-config.md)
- Learn about [Theme Customization](../user-guide/themes.md)
- Explore [Settings Interface](../user-guide/settings.md)
- Review [User Interface Guide](../user-guide/overview.md) 