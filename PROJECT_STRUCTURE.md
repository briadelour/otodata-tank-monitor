# Project Structure

This document describes the structure of the Otodata Propane Tank Monitor integration repository.

## Repository Layout

```
otodata-tank-monitor/
├── .github/
│   └── workflows/
│       ├── validate.yaml          # HACS validation workflow
│       └── release.yaml            # Automated release workflow
├── custom_components/
│   └── neevo/
│       ├── translations/
│       │   └── en.json            # English translations
│       ├── __init__.py            # Integration initialization
│       ├── config_flow.py         # UI configuration flow
│       ├── const.py               # Constants and configuration
│       ├── manifest.json          # Integration metadata
│       ├── sensor.py              # Sensor platform implementation
│       └── strings.json           # UI strings and translations
├── .gitignore                     # Git ignore rules
├── CHANGELOG.md                   # Version history and changes
├── CONTRIBUTING.md                # Contribution guidelines
├── EXAMPLES.md                    # Configuration examples
├── INSTALLATION.md                # Detailed installation guide
├── LICENSE                        # MIT License
├── QUICKSTART.md                  # Quick start guide
├── README.md                      # Main documentation
├── hacs.json                      # HACS metadata
└── info.md                        # Short description for HACS
```

## File Descriptions

### Core Integration Files

#### `custom_components/neevo/__init__.py`
- Integration setup and entry point
- Handles platform loading
- Manages integration lifecycle

#### `custom_components/neevo/config_flow.py`
- UI-based configuration flow
- Credential validation
- Error handling
- User input processing

#### `custom_components/neevo/const.py`
- Domain name
- Configuration keys
- API URLs and timeouts
- Default values
- State-specific pricing URLs
- Attribute names

#### `custom_components/neevo/sensor.py`
- Data update coordinator
- Tank sensor implementation
- Propane price sensor
- API communication
- State and attribute management

#### `custom_components/neevo/manifest.json`
- Integration metadata
- Version information
- Dependencies
- IoT class declaration
- Documentation links

#### `custom_components/neevo/strings.json`
- Configuration flow UI text
- Error messages
- Descriptions and placeholders

#### `custom_components/neevo/translations/en.json`
- English language translations
- Mirrors strings.json

### GitHub Workflows

#### `.github/workflows/validate.yaml`
- Runs HACS validation
- Checks integration structure
- Ensures HACS compatibility
- Runs on push, PR, and daily schedule

#### `.github/workflows/release.yaml`
- Automates release process
- Creates integration ZIP file
- Uploads to GitHub releases
- Triggered on release publication

### Documentation Files

#### `README.md`
- Main project documentation
- Feature overview
- Installation instructions
- Configuration guide
- Usage examples
- Troubleshooting section

#### `INSTALLATION.md`
- Step-by-step installation guide
- Otodata account setup
- HACS installation
- Integration configuration
- Propane pricing setup
- Verification steps

#### `QUICKSTART.md`
- 5-minute setup guide
- Prerequisites checklist
- Streamlined instructions
- Basic troubleshooting

#### `EXAMPLES.md`
- Dashboard card configurations
- Automation examples
- Template sensors
- Script examples
- Custom card configs

#### `CHANGELOG.md`
- Version history
- Feature additions
- Bug fixes
- Breaking changes

#### `CONTRIBUTING.md`
- Contribution guidelines
- Code style requirements
- Pull request process
- Development setup

### Metadata Files

#### `hacs.json`
- HACS integration metadata
- Minimum Home Assistant version
- Repository structure info

#### `info.md`
- Short description for HACS
- Quick feature overview
- Links to apps

#### `LICENSE`
- MIT License
- Usage permissions

#### `.gitignore`
- Python bytecode
- IDE files
- Home Assistant specific files

## Key Components

### 1. Configuration Flow
The integration uses Home Assistant's UI-based configuration:
- No YAML editing required
- Built-in credential validation
- Error handling and user feedback
- Optional propane pricing configuration

### 2. Data Update Coordinator
Manages data fetching and updates:
- 24-hour update interval
- Handles multiple tanks
- Optional price fetching
- Error handling and retry logic

### 3. Sensor Platform
Creates and manages sensors:
- Tank level sensors (one per tank)
- Optional propane price sensor
- State updates
- Attribute management

### 4. Multi-Tank Support
Automatically detects and creates sensors for multiple tanks:
- `sensor.neevo_tank_1`
- `sensor.neevo_tank_2`
- etc.

## Development Workflow

1. **Local Development**
   - Clone repository
   - Symlink to Home Assistant custom_components
   - Restart Home Assistant
   - Test changes

2. **Testing**
   - Verify integration loads
   - Test configuration flow
   - Check sensor updates
   - Review logs for errors

3. **Validation**
   - Run HACS validation
   - Check manifest structure
   - Verify strings/translations

4. **Release**
   - Update CHANGELOG.md
   - Update version in manifest.json
   - Create GitHub release
   - Automated ZIP creation

## HACS Requirements

The integration meets HACS requirements:
- ✅ Proper repository structure
- ✅ manifest.json with required fields
- ✅ hacs.json metadata file
- ✅ Valid Python code structure
- ✅ README documentation
- ✅ GitHub release automation

## API Integration

### Otodata API
- **Endpoint**: `https://ws.otodatanetwork.com/neevoapp/v1/DataService.svc/GetAllDisplayPropaneDevices`
- **Authentication**: HTTP Basic Auth
- **Method**: GET
- **Response**: JSON array of tank objects
- **Rate Limit**: None specified (using 24-hour polling)

### EIA Pricing API
- **Endpoint**: State-specific HTML pages
- **Method**: GET
- **Parsing**: Regex-based HTML scraping
- **Update Frequency**: Weekly (EIA updates)

## Security Considerations

- Credentials stored in Home Assistant's secure storage
- No plaintext passwords in configuration
- API calls use HTTPS
- Basic authentication over secure connection
- No credential logging

## Future Enhancements

Potential improvements tracked in CHANGELOG:
- Additional state pricing URLs
- Historical data tracking
- Custom update intervals
- Multiple account support
- Energy dashboard integration

## Support and Maintenance

- **Issues**: GitHub Issues tracker
- **Discussions**: Home Assistant Community
- **Updates**: HACS automatic update checks
- **Releases**: Semantic versioning
