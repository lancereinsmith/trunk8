# Themes and Customization

Trunk8 includes 25+ beautiful themes from Bootswatch, allowing you to customize the appearance of both the main interface and markdown rendering.

## Available Themes

### Theme Gallery

| Theme | Description | Best For |
|-------|-------------|----------|
| **Cerulean** | A calm blue sky | Professional, clean interfaces |
| **Cosmo** | An ode to Metro | Modern, flat design |
| **Cyborg** | Jet black and electric blue | Dark mode, tech focus |
| **Darkly** | Flatly in night mode | Dark theme preference |
| **Flatly** | Flat and modern | Minimalist design |
| **Journal** | Crisp like a new sheet of paper | Content-focused sites |
| **Litera** | The medium is the message | Typography emphasis |
| **Lumen** | Light and shadow | Subtle, refined look |
| **Lux** | A touch of class | Premium feel |
| **Materia** | Material is the metaphor | Google Material Design |
| **Minty** | A fresh feel | Light, refreshing |
| **Morph** | A modern take | Contemporary design |
| **Pulse** | A trace of purple | Vibrant accents |
| **Quartz** | A gem of a theme | Clean, crystalline |
| **Sandstone** | A touch of warmth | Friendly, approachable |
| **Simplex** | Mini and minimalist | Ultra-minimal |
| **Sketchy** | A hand-drawn look | Playful, informal |
| **Slate** | Shades of gunmetal gray | Professional dark |
| **Solar** | A spin on Solarized | Developer-friendly |
| **Spacelab** | Silvery and sleek | Futuristic |
| **Superhero** | The brave and the blue | Bold, heroic |
| **United** | Ubuntu orange and unique font | Ubuntu-inspired |
| **Vapor** | A subtle theme | Soft, muted tones |
| **Yeti** | A friendly foundation | Approachable, clean |
| **Zephyr** | Breezy and beautiful | Light, airy design |

## Changing Themes

### Via Web Interface

1. Log in to Trunk8
2. Click "Settings" in navigation
3. Select themes from dropdowns:
    - **UI Theme**: Main interface theme
    - **Markdown Theme**: Theme for rendered markdown
4. Click "Save Settings"
5. Changes apply immediately

### Via Configuration File

Edit `config/config.toml`:

```toml
[app]
theme = "darkly"           # Main UI theme
markdown_theme = "cerulean"  # Markdown rendering theme
```

Save the file - Trunk8 reloads automatically.

## Dual Theme System

### Why Two Themes?

Trunk8 allows separate themes for:

1. **UI Theme**: Admin interface, forms, navigation
2. **Markdown Theme**: Rendered markdown content

This allows:

- Dark UI with light markdown for readability
- Consistent branding with varied content
- User preference accommodation

### Example Combinations

| UI Theme | Markdown Theme | Effect |
|----------|----------------|---------|
| Darkly | Flatly | Dark interface, light content |
| Cosmo | Cosmo | Consistent modern look |
| Slate | Solar | Professional dark with coder-friendly content |
| Lux | Journal | Premium UI with readable content |

## Theme Features

### Responsive Design

All themes are:

- Mobile-friendly
- Tablet-optimized
- Desktop-perfect
- Print-ready

### Accessibility

Themes include:

- High contrast options
- Screen reader support
- Keyboard navigation
- ARIA labels

### Browser Support

Compatible with:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Customization Options

### CSS Overrides

Add custom CSS in `app/static/css/custom.css`:

```css
/* Custom brand colors */
.navbar {
    background-color: #ff6b6b !important;
}

/* Custom fonts */
body {
    font-family: 'Inter', sans-serif;
}

/* Custom link colors */
a {
    color: #4ecdc4;
}
```

Include in base template:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
```

### Logo Customization

Replace the logo:

1. Add your logo to `app/static/img/`
2. Update templates referencing `trunk8_logo.png`
3. Recommended: 200x200px PNG with transparency

### Favicon

Change the favicon:

1. Create favicon.ico
2. Place in `app/static/`
3. Update base template

## Theme Selection Guide

### For Business Use

Professional themes:

- **Cosmo**: Clean, modern
- **Flatly**: Minimalist
- **Lux**: Premium feel
- **United**: Ubuntu-inspired

### For Dark Mode

Dark themes:

- **Darkly**: Flat dark design
- **Cyborg**: High-tech dark
- **Slate**: Professional dark
- **Solar**: Developer-focused

### For Creativity

Unique themes:

- **Sketchy**: Hand-drawn style
- **Journal**: Paper-like
- **Pulse**: Purple accents
- **Vapor**: Vaporwave aesthetic

### For Readability

Content-focused:

- **Litera**: Typography-first
- **Journal**: Clean reading
- **Flatly**: Minimal distractions
- **Simplex**: Ultra-simple

## Advanced Theming

### Theme Variables

Bootswatch themes use CSS variables:

```css
:root {
    --bs-blue: #0d6efd;
    --bs-indigo: #6610f2;
    --bs-purple: #6f42c1;
    --bs-pink: #d63384;
    --bs-red: #dc3545;
    --bs-orange: #fd7e14;
    --bs-yellow: #ffc107;
    --bs-green: #198754;
    --bs-teal: #20c997;
    --bs-cyan: #0dcaf0;
}
```

Override in custom CSS:
```css
:root {
    --bs-primary: #ff6b6b;
    --bs-secondary: #4ecdc4;
}
```

### Component Styling

Target specific components:

```css
/* Custom button styles */
.btn-primary {
    border-radius: 50px;
    text-transform: uppercase;
}

/* Custom card styles */
.card {
    border: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

/* Custom navbar */
.navbar-brand {
    font-weight: bold;
    font-size: 1.5rem;
}
```

### JavaScript Theming

Add theme toggle:

```javascript
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}
```

## Theme Development

### Creating Custom Themes

1. Start with a Bootswatch theme
2. Modify variables
3. Compile with Sass
4. Test across devices

### Theme Structure

```scss
// _variables.scss
$primary: #ff6b6b;
$secondary: #4ecdc4;
$font-family-base: 'Inter', sans-serif;

// _bootswatch.scss
.navbar {
    border-radius: 0;
}

.btn {
    text-transform: uppercase;
}
```

### Testing Themes

Check:

- All page types
- Form elements
- Tables and lists
- Mobile responsiveness
- Print styling

## Troubleshooting

### Theme Not Changing

1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check config/config.toml syntax
4. Verify theme name spelling

### Broken Styling

- Check custom CSS for errors
- Disable browser extensions
- Try incognito mode
- Verify CDN accessibility

### Performance Issues

- Minimize custom CSS
- Use browser caching
- Optimize images
- Enable compression

## Best Practices

### Do's

- ✅ Test on multiple devices
- ✅ Check accessibility
- ✅ Keep customizations minimal
- ✅ Document custom changes
- ✅ Backup before major changes

### Don'ts

- ❌ Override too many styles
- ❌ Use !important excessively
- ❌ Forget mobile testing
- ❌ Ignore performance
- ❌ Break accessibility


## Resources

### Learning More

- [Bootswatch Themes](https://bootswatch.com/)
- [Bootstrap Documentation](https://getbootstrap.com/)
- [CSS Variables Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)


## Next Steps

- Browse [available themes](https://bootswatch.com/)
- Configure [settings](settings.md)
- Learn about [custom development](../development/architecture.md)
- Explore [API documentation](../api/overview.md) 