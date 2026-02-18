# Pogo Pin (Test Probe) Hardware Guide

**OpenFixture Pogo Pin Selection and Specification**  
**Last Updated**: February 18, 2026

---

## 📖 Overview

Pogo pins (spring-loaded test probes) are the critical contact elements in OpenFixture test fixtures. They provide reliable electrical connection to PCB test points while allowing repeated insertion/removal cycles. This guide covers pogo pin selection, specifications, installation, and maintenance for both budget-friendly and professional-grade options.

OpenFixture is designed to work with standard pogo pin series available from multiple suppliers worldwide. The fixture automatically calculates optimal compression and hole placement based on your chosen pogo pin specifications.

---

## 📐 Digole Pogo Pin Series Comparison

Digole offers four pogo pin series with different barrel diameters and lengths to suit various applications. All series use a two-part system with interchangeable probe pins and receptacles.

**Source**: [Digole P50/P75/P100/P160 Pogo Pins](https://www.digole.com/index.php?productID=1228)

### Series Specifications Table

| Series | Barrel Ø | Total Length | Spring Stroke | Receptacle | Current Rating | Best For |
|--------|----------|--------------|---------------|------------|----------------|----------|
| **P50** | 0.68mm (0.027") | 16.55mm | 2.65mm | R50 | 0.5-1.5A | Ultra-fine pitch (<0.3mm pads), micro-BGA |
| **P75** | 1.02mm (0.040") | 16.50mm | 2.50mm | R75 | 1.5-3A | **Most common**, 0402-0805 pads, general use |
| **P100** | 1.36mm (0.054") | 33.30mm | 6.50mm | R100 | 2-4A | Deep fixtures, high current, thick PCBs |
| **P160** | 1.36mm (0.054") | 24.50mm | 4.00mm | R160 | 2-4A | Medium depth, high current applications |

**Recommended**: **P75 series** offers the best balance of cost, availability, and performance for typical PCB testing applications.

### Pogo Pin Tip Styles

Digole pogo pins use a naming convention where the **1st letter** indicates tip type and the **2nd number** indicates tip diameter (larger number = larger diameter).

#### Tip Type Reference

| Code | Tip Style | Profile | Best Application | Image Reference |
|------|-----------|---------|------------------|-----------------|
| **A** | Sharp Point | Conical, very fine point | Ultra-small pads (<0.5mm), fine-pitch ICs, 01005 components | See [Digole Tip Chart](https://www.digole.com/index.php?productID=1228) |
| **B** | Rounded | Hemispherical dome | Through-hole pins, general purpose, won't scratch pads | ![Type B](https://www.digole.com/index.php?productID=1228) |
| **D** | Flat | Flat circular face | Large pads (>1.5mm), high current, maximum contact area | ![Type D](https://www.digole.com/index.php?productID=1228) |
| **E** | Crown | Star/crown with center point | **Most versatile**, self-aligning, 0402-0805 components | ![Type E](https://www.digole.com/index.php?productID=1228) |
| **F** | Rounded (variant) | Smooth hemisphere | Similar to B, different geometry | ![Type F](https://www.digole.com/index.php?productID=1228) |
| **G** | Large Crown | Wide star pattern | Large pads, good centering, stable contact | ![Type G](https://www.digole.com/index.php?productID=1228) |
| **H** | Extended Crown | Long reach with crown tip | Deep recessed pads, components in cavities | ![Type H](https://www.digole.com/index.php?productID=1228) |
| **J** | Special Profile | Custom geometry | Specific applications (consult datasheet) | ![Type J](https://www.digole.com/index.php?productID=1228) |
| **LM** | Long Tip | Extended reach | Test points in confined spaces | ![Type LM](https://www.digole.com/index.php?productID=1228) |
| **Q** | Concave | Cup-shaped | Dome-shaped solder bumps, spring pins | ![Type Q](https://www.digole.com/index.php?productID=1228) |
| **T** | Serrated | Toothed/grooved | Penetrates oxide, reliable contact on aged boards | ![Type T](https://www.digole.com/index.php?productID=1228) |

**Tip Diameter Codes**:
- **1, 2, 3, 4, 5**: Diameter indicators (e.g., E2 is smaller than E3)
- Larger numbers = larger tip diameter = more contact area = higher current capacity

**Example Model Numbers**:
- `P75-A2`: P75 series, A (sharp point) tip, size 2 diameter
- `P75-E2`: P75 series, E (crown) tip, size 2 diameter  
- `P100-D3`: P100 series, D (flat) tip, size 3 diameter

### Visual Tip Profile Comparison

```
A (Sharp):        B (Round):        D (Flat):         E (Crown):
    /\               ___                ___            /\/\/\
   /  \             /   \            _______           \ | /
  /    \           |     |          |_______|          _\|/_
 -------          -------           -------            -------

F (Round):        G (Lg Crown):    H (Extended):     T (Serrated):
   ___              /\/\             /\               /\/\/\
  /   \            /    \           /  \             /\/\/\/\
 |     |          /      \         |    |           /\/\/\/\/\
 -------         ---------         |    |           -----------
                                   ------
```

**Note**: Actual tip profiles may vary slightly by manufacturer. Always verify dimensions with supplier datasheet.

---

## 🎯 Quick Selection Guide

| Application | Recommended Series | Tip Style | Length | Cost/Point | Cycle Life |
|-------------|-------------------|-----------|--------|------------|------------|
| **Ultra-Fine Pitch (<0.3mm pads)** | P50-A2 or P50-E2 | Sharp/Crown | 16.5mm | $0.35 | 8k-30k |
| **Prototype Testing** | P75-E2 or P75-B1 | Crown/Round | 16-24mm | $0.30 | 10k-50k |
| **Production Testing** | Fixtest 100 | Crown/Round | 25-30mm | $3.50 | 100k+ |
| **High Current (2-4A)** | P100-D2 or P160-D2 | Flat | 24-33mm | $0.45 | 15k-60k |
| **Deep Fixtures (>10mm)** | P100-E2 or P100-D3 | Crown/Flat | 33mm | $0.45 | 15k-60k |
| **Small Pads (<0.5mm)** | P75-A2 or P50-A2 | Sharp Point | 16-17mm | $0.30-35 | 8k-50k |
| **Large Pads (>1.5mm)** | P75-D2/D3 or P100-D2 | Flat | 20-33mm | $0.30-45 | 10k-60k |
| **Through-Hole Pins** | P75-B1 | Rounded | 16.5mm | $0.30 | 10k-50k |

### Series Selection by Requirement

**By Pad Size:**
- **<0.3mm pads**: P50 series (ultra-fine pitch)
- **0.3-1.5mm pads**: P75 series (most common)
- **>1.5mm pads**: P100 or P160 series (high current capability)

**By Current Requirement:**
- **<1.5A**: P50 or P75 series
- **1.5-3A**: P75 or P160 series  
- **2-4A**: P100 or P160 series (flat tips recommended)

**By Fixture Depth:**
- **<6mm stack**: P75 series (16.5mm) or P160 (24.5mm)
- **6-10mm stack**: P160 (24.5mm) or P100 (33.3mm)
- **>10mm stack**: P100 series (33.3mm) only

**By Budget:**
- **Lowest cost**: P75 series (~$0.30/point)
- **Best value**: P75 series (cost vs performance)
- **Highest performance/longevity**: Fixtest 100 (~$3.50/point)

---

## 💰 P75 Series (Budget-Friendly)

### Overview

The P75 series is an economical option ideal for prototypes, low-volume testing, and hobbyist projects. With prices starting at $0.16 per pin, they offer excellent value for occasional use while still providing reliable contact.

### Technical Specifications

- **Barrel Diameter**: 1.02mm (0.040")
- **Tip Styles**: Sharp pointed, rounded, flat, crown
- **Total Length Range**: 16.5-33.3mm (depends on model)
- **Spring Travel**: 1.0-3.0mm typical
- **Current Rating**: 1.5-3A (varies by tip style and contact area)
- **Contact Resistance**: <50mΩ
- **Cycle Life**: 10,000-50,000 cycles
- **Operating Temperature**: -20°C to +80°C
- **Spring Force**: 50-100g typical (varies by length)
- **Price**: $0.16-$0.22 USD per pin + ~$0.10 for receptacle

### Available Models

| Model | Length | Tip Style | Tip Diameter | Best For | Price |
|-------|--------|-----------|--------------|----------|-------|
| **P75-A2** | 16.5mm | Sharp Point | 0.4mm | Very small pads (<0.5mm), fine-pitch components | $0.16 |
| **P75-B1** | 16.5mm | Rounded | 0.8mm | Through-hole connector pins, general purpose | $0.16 |
| **P75-D2** | 20.0mm | Flat | 1.0mm | Large pads (>1.5mm), high current applications | $0.22 |
| **P75-D3** | 22.0mm | Flat | 1.0mm | Large pads, extra reach for thick PCBs | $0.22 |
| **P75-E2** | 24.0mm | Crown | ~0.6mm | **General purpose**, 0402-0805 pads, most common | $0.22 |
| **P75-F1** | 26.5mm | Rounded | 0.8mm | Extended reach, deep fixtures | $0.16 |
| **P75-G2** | 33.3mm | Large Crown | ~0.8mm | Very thick fixtures, special applications | $0.22 |

### Recommended Models for Common Applications

**Best General Purpose: P75-E2**
- 24mm length fits most fixture designs
- Crown tip works well for 0402 through 0805 component pads
- Good balance of reach and stability
- Most versatile choice for mixed PCB designs

**Best for Connectors: P75-B1**
- 16.5mm length is compact
- Rounded tip enters through-hole pins smoothly
- Won't damage plated holes
- Ideal for testing USB, HDMI, pin headers

**Best for Fine Pitch: P75-A2**
- Sharp 0.4mm point for precise contact
- Excellent for 0201 components and small test pads
- Higher contact resistance due to small area (not for high current)
- Perfect for dense BGA test points

### Receptacles

P75 series uses two-part construction:

1. **Receptacle (Holder)**: ~$0.10 each
   - Press-fit installation into acrylic/plywood
   - Barrel OD: 1.5mm typical (verify with supplier)
   - Depth: Varies by model (8-15mm typical)
   - Material: Brass or copper alloy

2. **Probe Pin (Plunger)**: $0.16-$0.22 each (prices above)
   - Spring-loaded mechanism
   - Replaceable wear component
   - Push-fit into receptacle

### Installation

1. **Drill holes** in fixture plate (1.5mm diameter typical, verify with your receptacle specs)
2. **Press-fit receptacles** from inside of fixture plate
3. **Insert probe pins** into receptacles from outside
4. **Test compression** by closing fixture (should feel 1-1.5mm travel)

### Maintenance

- **Replacement interval**: Every 5,000-10,000 cycles
- **Signs of wear**: 
  - Flattened or damaged tips
  - Reduced spring force (weak contact)
  - Intermittent connections
  - Visible corrosion or discoloration
- **Tip**: Buy probe pins in bulk, keep receptacles installed permanently

### Suppliers

**Digole Digital Solutions** (P50, P75, P100, P160 series):
- **All Series**: [P50/P75/P100/P160 Main Product Page](https://www.digole.com/index.php?productID=1228) - Specifications and tip style images
- **P75 Series Catalog**: [P75 Individual Models](https://www.digole.com/index.php?categoryID=115) - Direct from manufacturer
- **Ordering**: Contact through website for bulk pricing and custom configurations
- **Tip Style Reference**: See [product page](https://www.digole.com/index.php?productID=1228) for tip profile images

**Alternative Sources:**
- **AliExpress**: Search "P75 pogo pin" or "P100 pogo pin" - Bulk pricing (50-100 pcs), verify specifications
- **eBay**: Various resellers - Good for small quantities, always verify dimensions before ordering

### Cost Analysis

**Per Test Point Cost**: $0.26-$0.32 USD
- Receptacle: $0.10
- Probe pin: $0.16-$0.22

**100 Test Point Fixture**: ~$30 USD in pogo pins
**Cost per 1,000 cycles**: $0.03 (assuming 10,000 cycle life)

---

## 🔬 P50 Series (Ultra-Fine Pitch)

### Overview

The P50 series is the smallest Digole pogo pin, designed for ultra-fine pitch applications where the P75 series is too large. With a 0.68mm barrel diameter, these probes can test very small pads and densely packed components like micro-BGAs and 01005 passives.

### Technical Specifications

- **Barrel Diameter**: 0.68mm (0.027") - smallest in Digole lineup
- **Total Length**: 16.55mm
- **Spring Stroke**: 2.65mm
- **Receptacle**: R50 (matched to 0.68mm barrel)
- **Current Rating**: 0.5-1.5A (limited by small contact area)
- **Contact Resistance**: <80mΩ (higher due to small tip)
- **Cycle Life**: 8,000-30,000 cycles (smaller parts = shorter life)
- **Operating Temperature**: -20°C to +80°C
- **Spring Force**: 30-60g typical (lower force for delicate pads)
- **Price**: $0.18-$0.25 USD per pin + ~$0.12 for R50 receptacle

### When to Use P50

**Ideal For:**
- Micro-BGA test points (<0.3mm pad diameter)
- 01005 and 0201 component testing
- Ultra-high density PCBs (>1000 test points/dm²)
- Fine-pitch flex circuits
- Semiconductor test fixtures

**Not Recommended For:**
- High current testing (>1A per pin)
- Large pads (use P75 or P100 instead)
- Rough handling environments (fragile due to small size)
- General purpose testing (P75 more economical)

### Available Tip Styles

Common P50 models include:
- **P50-A1/A2**: Sharp point - for ultra-small pads
- **P50-B1**: Rounded - less pad wear
- **P50-E1/E2**: Crown - self-centering
- **P50-F1**: Rounded variant

*(Not all tip styles available in P50; consult supplier for current catalog)*

### Installation Considerations

- **Hole diameter**: ~1.0mm (smaller than P75)
- **Alignment critical**: Tight tolerances required
- **Fragile**: Handle with care during installation
- **Recommended tool**: Precision arbor press or alignment jig
- **Test before full assembly**: Verify all probes return smoothly

### Cost Analysis

**Per Test Point Cost**: $0.30-$0.37 USD
- R50 Receptacle: $0.12
- P50 Probe pin: $0.18-$0.25

**Higher cost per point than P75, but necessary for ultra-fine applications**

---

## 💪 P100 Series (Heavy Duty / Extended Reach)

### Overview

The P100 series offers extended length (33.3mm) and larger barrel diameter (1.36mm) for applications requiring deep reach or higher current capacity. The increased spring stroke (6.5mm) provides more compliance for warped PCBs or fixtures with greater stack-up variation.

### Technical Specifications

- **Barrel Diameter**: 1.36mm (0.054") - 33% larger than P75
- **Total Length**: 33.30mm - longest standard Digole probe
- **Spring Stroke**: 6.50mm - excellent compliance
- **Receptacle**: R100 (matched to 1.36mm barrel)
- **Current Rating**: 2-4A continuous (varies by tip contact area)
- **Contact Resistance**: <40mΩ (lower due to larger contact)
- **Cycle Life**: 15,000-60,000 cycles
- **Operating Temperature**: -20°C to +80°C
- **Spring Force**: 80-150g typical (higher force for reliable contact)
- **Price**: $0.25-$0.35 USD per pin + ~$0.15 for R100 receptacle

### When to Use P100

**Ideal For:**
- Deep fixture designs (>10mm stack height)
- High current testing (2-4A per probe)
- Large test pads (>2mm diameter)
- Power supply testing (voltage rails, ground)
- Thick PCBs (>3mm) or multiple PCB stack testing
- Fixtures with significant compliance requirements

**Advantages Over P75:**
- Longer reach accommodates deep fixtures
- Higher current capacity (2-4A vs 1.5-3A)
- Better compliance (6.5mm stroke vs 2.5mm)
- More robust (less prone to bending)

**Trade-offs:**
- Higher cost per probe
- Requires larger holes in fixture plate (~2.0mm)
- Higher spring force (may require mechanical advantage for >50 probes)
- Minimum pad spacing increases (~3.5mm vs 2.5mm for P75)

### Available Tip Styles

Common P100 models include:
- **P100-D2/D3**: Flat tip - maximum current capacity
- **P100-E2/E3**: Crown tip - general purpose
- **P100-B1**: Rounded - through-hole testing
- **P100-G2**: Large crown - large pad centering

### Installation Considerations

- **Hole diameter**: ~2.0mm (verify with R100 receptacle specs)
- **Deeper receptacle**: R100 is longer, ensure adequate fixture plate thickness
- **Higher insertion force**: Use arbor press, not manual installation
- **Spring force management**: Consider leverage or cam mechanism for >30 probes
- **Pad spacing**: Minimum 3.5mm center-to-center recommended

### Cost Analysis

**Per Test Point Cost**: $0.40-$0.50 USD
- R100 Receptacle: $0.15
- P100 Probe pin: $0.25-$0.35

**Best value for high-current or extended-reach applications**

---

## ⚡ P160 Series (Medium Reach / High Current)

### Overview

The P160 series provides a middle ground between P75 and P100, offering the same robust 1.36mm barrel diameter as P100 but with shorter length (24.5mm) and moderate stroke (4.0mm). Ideal when you need higher current capacity but don't require the full reach of P100.

### Technical Specifications

- **Barrel Diameter**: 1.36mm (0.054") - same as P100
- **Total Length**: 24.50mm - between P75 (16.5mm) and P100 (33.3mm)
- **Spring Stroke**: 4.00mm - good compliance
- **Receptacle**: R160 (matched to 1.36mm barrel)
- **Current Rating**: 2-4A continuous (same as P100)
- **Contact Resistance**: <40mΩ
- **Cycle Life**: 15,000-60,000 cycles
- **Operating Temperature**: -20°C to +80°C
- **Spring Force**: 70-120g typical
- **Price**: $0.22-$0.32 USD per pin + ~$0.15 for R160 receptacle

### When to Use P160

**Ideal For:**
- High current testing with moderate fixture depth
- Power delivery test points (USB-C, battery connections)
- Medium-depth fixtures (5-8mm stack height)
- Applications where P75 current is insufficient but P100 is too long
- Cost-effective upgrade from P75 for current capacity

**Comparison to P100:**
- **Shorter** (24.5mm vs 33.3mm) - more compact fixtures
- **Less stroke** (4.0mm vs 6.5mm) - adequate for most applications
- **Lower cost** (~$0.37 vs ~$0.45 per point)
- **Same current rating** (2-4A)
- **Same barrel diameter** (1.36mm) - interchangeable receptacles with P100

### Available Tip Styles

Common P160 models include:
- **P160-D2/D3**: Flat tip - high current
- **P160-E2/E3**: Crown tip - versatile
- **P160-B1**: Rounded - general testing
- **P160-F1**: Rounded variant

### Installation Considerations

- **Hole diameter**: ~2.0mm (same as P100, uses similar R160 receptacle)
- **Interchangeable**: R100 and R160 receptacles may be compatible (verify with supplier)
- **Spring force**: Lower than P100, easier to close fixture
- **Space efficiency**: Shorter profile allows more compact fixture designs

### Cost Analysis

**Per Test Point Cost**: $0.37-$0.47 USD
- R160 Receptacle: $0.15
- P160 Probe pin: $0.22-$0.32

**Best value for high-current testing in compact fixtures**

---

## 🏭 Fixtest Series 100 (Professional Grade)

### Overview

Fixtest Series 100 is a professional-grade test probe system designed for production environments. With 100,000+ cycle life and gold-plated contacts, these probes offer superior reliability and longevity. Higher initial cost is offset by extended lifespan in high-volume testing applications.

### Technical Specifications

- **Series**: 100 (standard industrial test probe series)
- **Material**: Beryllium copper spring, hardened steel barrel
- **Contact Finish**: Gold plated for low resistance and corrosion prevention
- **Receptacle Length**: 29.6mm (S 100.00-L model)
- **Spring Force**: Varies by model (typically 80-150g)
- **Cycle Life**: 100,000+ cycles (high durability)
- **Current Rating**: 3A continuous, 5A peak
- **Contact Resistance**: <30mΩ (gold plating)
- **Operating Temperature**: -40°C to +125°C
- **Precision**: ±0.05mm alignment tolerance
- **Vibration Resistance**: High (suitable for automated test equipment)
- **Price**: ~$1.50 probe + ~$2.00 receptacle = **$3.50 per test point**

### Key Features

**Gold-Plated Contacts:**
- Superior electrical conductivity
- Corrosion resistant
- Maintains low contact resistance over lifecycle
- Ideal for sensitive measurements

**Beryllium Copper Spring:**
- Excellent spring properties
- Maintains force over 100,000+ cycles
- Temperature stable
- High fatigue resistance

**Interchangeable Probe Tips:**
- Multiple tip styles available
- Easy field replacement
- Consistent receptacle installation
- Reduces maintenance downtime

**Precision Alignment:**
- ±0.05mm tolerance
- Critical for automated test systems
- Ensures repeatable contact
- Reduces PCB pad wear

### Available Models

Fixtest Series 100 offers multiple probe and receptacle combinations:

**Receptacle Model:**
- **S 100.00-L**: 29.6mm length, solder-mount style
- Gold-plated contact barrel
- Designed for PCB mounting or fixture plate installation

**Probe Styles (Interchangeable):**
- **Crown tip**: General purpose, most common
- **Flat tip**: High current applications
- **Pointed tip**: Fine pitch applications
- **Rounded tip**: Through-hole testing

*(Consult TME catalog for specific probe model numbers)*

### Installation Methods

**Method 1: Press-Fit (Recommended for Fixtures)**
1. Drill 2.0-2.2mm holes in fixture plate
2. Press receptacles from inside
3. Secure with retaining clips or adhesive if needed
4. Insert probes from outside

**Method 2: Solder-Mount (For PCB Integration)**
1. Design PCB with landing pads
2. Use fixture plate as alignment template
3. Solder receptacles to PCB
4. Mount PCB assembly to fixture

### Maintenance

- **Replacement interval**: Every 50,000-100,000 cycles
- **Inspection frequency**: Every 10,000 cycles or quarterly
- **Cleaning**: Isopropyl alcohol wipe (monthly in production)
- **Signs of wear**: 
  - Gold plating worn through (brass visible)
  - Reduced spring force
  - Physical tip damage
  - Contact resistance >50mΩ

### Suppliers

- **TME (Transfer Multisort Elektronik)**: [Fixtest S 100.00-L](https://www.tme.eu/pl/details/s100.00-l/igly-testowe/fixtest/s-100-00-l/) - European distributor
- **Digi-Key**: Search "spring loaded test probe" or "ICT probe"
- **Mouser Electronics**: Search "pogo pin" filter by Fixtest brand
- **Direct from Fixtest**: Contact manufacturer for volume pricing

### Cost Analysis

**Per Test Point Cost**: $3.50 USD
- Receptacle: $2.00
- Probe pin: $1.50

**100 Test Point Fixture**: ~$350 USD in pogo pins
**Cost per 1,000 cycles**: $0.035 (assuming 100,000 cycle life)

**ROI Calculation:**
- Breakeven vs P75: ~12,000 test cycles
- Best choice for fixtures with >20,000 expected cycles
- Consider for any production application

---

## 🏆 Alternative Professional Series

### Mill-Max (USA)

**Website**: [mill-max.com](https://www.mill-max.com/)

**Key Products:**
- Spring-loaded connectors and test probes
- Very high quality American manufacturing
- Price: $3-6 per test point
- Excellent technical documentation and support
- Variety of mounting styles (press-fit, solder, screw-mount)

**Best For**: Aerospace, medical, military applications requiring US-sourced components

### Harwin (UK)

**Website**: [harwin.com](https://www.harwin.com/)

**Key Products:**
- Datamate test probe series
- Automotive-grade reliability
- Price: $2-5 per test point
- High vibration resistance
- IP67 sealed options available

**Best For**: Automotive, harsh environment testing

### Preci-Dip (Switzerland)

**Website**: [precidip.com](https://www.precidip.com/)

**Key Products:**
- High-precision test and burn-in probes
- Swiss manufacturing precision
- Price: $4-8 per test point
- Exceptional repeatability (±0.02mm)
- Long life (150,000+ cycles)

**Best For**: Semiconductor testing, high-reliability applications

---

## ⚙️ OpenFixture Configuration

### Configuration File Setup

Set pogo pin parameters in `fixture_config.toml`:

```toml
[hardware]
# Uncompressed length of pogo pin (measured from receptacle base to tip)
# This is the most critical parameter - measure your actual pogo pins!

# For P75-A2 or P75-B1 (16.5mm)
pogo_uncompressed_length_mm = 16.5

# For P75-E2 (24mm) - RECOMMENDED for general use
# pogo_uncompressed_length_mm = 24.0

# For P75-D2 (20mm)
# pogo_uncompressed_length_mm = 20.0

# For Fixtest S 100.00-L (29.6mm receptacle)
# pogo_uncompressed_length_mm = 29.6

# For Mill-Max or other custom probes
# pogo_uncompressed_length_mm = [measure your probe]
```

### Automatic Calculations

OpenFixture automatically computes:

1. **Compressed length**: Based on fixture stack-up (material + PCB thickness)
2. **Target compression**: Typically 1.0-1.5mm for optimal spring force
3. **Hole diameter**: Default 0.75mm radius (1.5mm diameter) for 1.02mm barrel
4. **Hole pattern**: Exact X,Y coordinates for each test point

### Compression Explained

**Compression** = Uncompressed Length - (Top Plate Thickness + Air Gap + PCB Thickness)

**Example Calculation:**
```
Pogo Pin: P75-E2 (24mm uncompressed)
Material: 3mm acrylic
PCB: 1.6mm
Air Gap: 0.5mm (target)

Compressed Length = 24mm - (3mm + 0.5mm + 1.6mm) = 18.9mm
Compression = 24mm - 18.9mm = 5.1mm

Note: 5.1mm is TOO MUCH compression!
Solution: Use 2-layer top plate (6mm total) for proper 1.5mm compression
```

OpenFixture handles these calculations automatically in the OpenSCAD model.

### Validation

After generating fixture DXF files:

1. **Check hole spacing**: Minimum 2.5mm center-to-center
2. **Verify compression**: Use OpenSCAD preview
3. **Test cut**: Cut one test plate and verify receptacle fit
4. **Dry fit**: Assemble with receptacles, check alignment before inserting probes

---

## 🔧 Installation Guide

### Two-Part Pogo Pin System

All recommended pogo pins use a two-part system:

1. **Receptacle (Holder)**: Permanent installation in fixture
2. **Probe Pin (Plunger)**: Spring-loaded, replaceable component

### Installation Steps

#### Step 1: Prepare Fixture Plates

OpenFixture generates two top plates with identical hole patterns:
- `head_base`: Lower guide plate
- `head_top`: Upper alignment plate

Both have pogo pin holes at exact test point positions.

#### Step 2: Install Receptacles

**For Press-Fit Receptacles (Acrylic/Plywood fixtures):**

1. Identify receptacle orientation (usually wider end is top)
2. Position receptacle on **inside** of fixture plate
3. Use arbor press or carefully tap with non-marring mallet
4. Press until receptacle shoulder seats against plate surface
5. Verify receptacle is perpendicular to plate (not tilted)
6. Repeat for all test points

**Tips:**
- Use drill jig or CNC for accurate hole placement
- Start with 1.5mm holes for P75 series
- If too tight: Carefully ream to 1.6mm
- If too loose: Use cyanoacrylate (CA glue) around receptacle barrel

**For Solder-Mount Receptacles:**

1. Cut PCB to match fixture plate dimensions
2. Solder receptacles to PCB using through-hole technique
3. Mount PCB assembly to acrylic plate
4. Provides most rigid installation

#### Step 3: Install Probe Pins

1. Insert probe pin into receptacle from **outside** of fixture
2. Should slide smoothly with slight resistance
3. Push until pin bottoms out in receptacle
4. Test spring action by pressing pin (should return smoothly)
5. Repeat for all positions

#### Step 4: Alignment Verification

1. Close fixture (without PCB)
2. All probe pins should be same height ±0.2mm
3. Check for bent or misaligned pins
4. Verify smooth opening/closing action

### Compression Settings

**Optimal Compression**: 1.0-1.5mm

This provides:
- Sufficient contact force (50-100g typical)
- Reliable electrical connection
- Reasonable closing force
- Long probe life

**Troubleshooting Compression:**

| Symptom | Cause | Solution |
|---------|-------|----------|
| Intermittent contact | Too little compression (<0.5mm) | Use thinner material or longer probes |
| Difficult to close | Too much compression (>2mm) | Use thicker material or shorter probes |
| Pins bind/stick | Misalignment | Check receptacle perpendicularity |
| Uneven contact | Height variation | Check fixture plate flatness |

---

## 🔄 Maintenance and Replacement

### Inspection Schedule

**Weekly (Heavy Use):**
- Visual inspection for damaged tips
- Test fixture closing force (should be consistent)
- Check for bent or misaligned probes

**Monthly:**
- Clean probe tips with isopropyl alcohol and lint-free cloth
- Check contact resistance (use multimeter)
- Inspect for corrosion or discoloration

**Quarterly:**
- Full probe replacement if near cycle limit
- Deep clean receptacles
- Verify alignment with precision gauge

### Probe Replacement

**When to Replace:**
- Reached recommended cycle count
- Visible tip damage (flattened, chipped, corroded)
- Increased contact resistance (>100mΩ for P75, >50mΩ for Fixtest)
- Weak spring force (probe doesn't return smoothly)
- Intermittent connections during testing

**How to Replace:**

1. Remove old probe pin (pull straight out)
2. Inspect receptacle for damage or debris
3. Clean receptacle with compressed air
4. Insert new probe pin
5. Test spring action
6. Mark fixture with replacement date

### Receptacle Maintenance

Receptacles last much longer than probe pins:
- **P75 series**: 50,000-100,000 cycles for receptacles
- **Fixtest 100**: 200,000+ cycles for receptacles

**Replace receptacles when:**
- Physical damage (cracked, deformed)
- Probe pins won't stay in place (worn retention)
- Excessive play in probe pin (worn internal bore)

### Spare Parts Planning

**Recommended Spares:**

For 100 test point fixture:
- **Probe pins**: 20 spares (20% of total)
- **Receptacles**: 5 spares (5% of total)
- Store in sealed bag or container
- Label with part number and date received

**Bulk Ordering:**

P75 series is often cheaper in bulk:
- 50 pieces: 10-15% discount
- 100 pieces: 20-25% discount
- 500 pieces: 30-40% discount

---

## 📊 Performance Comparison

### Digole Series Comparison (P50 vs P75 vs P100 vs P160)

| Parameter | P50 | P75 | P100 | P160 |
|-----------|-----|-----|------|------|
| **Barrel Diameter** | 0.68mm | 1.02mm | 1.36mm | 1.36mm |
| **Total Length** | 16.55mm | 16.50mm | 33.30mm | 24.50mm |
| **Spring Stroke** | 2.65mm | 2.50mm | 6.50mm | 4.00mm |
| **Current Rating** | 0.5-1.5A | 1.5-3A | 2-4A | 2-4A |
| **Cost/Point** | $0.35 | $0.30 | $0.45 | $0.40 |
| **Cycle Life** | 8k-30k | 10k-50k | 15k-60k | 15k-60k |
| **Min Pad Size** | 0.2mm | 0.4mm | 0.8mm | 0.8mm |
| **Min Spacing** | 1.5mm | 2.5mm | 3.5mm | 3.5mm |
| **Best For** | Micro-BGA | General use | Deep/High-I | Medium depth |
| **Receptacle** | R50 | R75 | R100 | R160 |

**Recommendations by Application:**
- **Ultra-fine pitch (<0.3mm pads)**: P50 only option
- **General purpose (0.4-1.5mm pads)**: P75 best value
- **High current (2-4A)**: P100 or P160 (P160 if space limited)
- **Deep fixtures (>10mm)**: P100 only option
- **Budget-conscious**: P75 lowest cost per point

### Digole vs Professional: P75 vs Fixtest 100

| Parameter | P75 Series | Fixtest 100 | Winner |
|-----------|------------|-------------|--------|
| **Initial Cost** | $0.30/point | $3.50/point | P75 |
| **Cycle Life** | 10k-50k | 100k+ | Fixtest |
| **Cost/1k Cycles** | $0.03 | $0.035 | P75 (close) |
| **Contact Resistance** | <50mΩ | <30mΩ | Fixtest |
| **Current Rating** | 1.5-3A | 3A continuous | Fixtest |
| **Operating Temp** | -20°C to +80°C | -40°C to +125°C | Fixtest |
| **Alignment Precision** | ±0.1mm | ±0.05mm | Fixtest |
| **Availability** | Good | Excellent | Fixtest |
| **Lead Time** | 2-4 weeks (China) | 1-2 days (stock) | Fixtest |

### When to Choose Each Series

**Choose P50 when:**
- Pad size <0.3mm (no other option works)
- Ultra-high density (>1000 test points/dm²)
- Micro-BGA or 01005 components
- Cost is secondary to functionality

**Choose P75 when:**
- Budget is primary concern
- Pad size 0.4-1.5mm (covers 95% of applications)
- Prototype or low-volume testing (<50k cycles total)
- General purpose fixture
- **This is the default choice for most users**

**Choose P100 when:**
- Need >10mm reach (deep fixture stacks)
- High current required (2-4A per probe)
- Extra compliance needed (warped PCBs, thick boards)
- Long-term reliability more important than cost

**Choose P160 when:**
- High current (2-4A) but space is limited
- Moderate fixture depth (5-8mm)
- P75 current insufficient, P100 is overkill
- Cost-effective upgrade from P75 for power testing

**Choose Fixtest 100 when:**
- Production environment (>75k cycles total)
- Automated test equipment
- Gold-plated contacts required
- Precision alignment critical (±0.05mm)
- Extended temperature range needed
- Budget allows for higher initial investment

### Lifecycle Cost Analysis

**Scenario: 50,000 test cycles over 2 years**

**Option 1: P75 Series**
- Initial investment: 100 points × $0.30 = $30
- Replacements: 5 cycles × 20 probes × $0.20 = $20
- Total cost: $50
- Cost per cycle: $0.001

**Option 2: Fixtest 100**
- Initial investment: 100 points × $3.50 = $350
- Replacements: 0 (within lifecycle)
- Total cost: $350
- Cost per cycle: $0.007

**Recommendation**: P75 is more economical for <75,000 cycles

---

## 🎓 Best Practices

### PCB Design for Testing

**Pad Design:**
- Minimum size: 0.5mm diameter (prefer 0.8-1.0mm)
- Remove **both** solder mask and paste mask
- Use circular or oval pads (better than square)
- Add test point silkscreen labels (TP1, TP2, etc.)

**Test Point Placement:**
- Minimum 2.5mm spacing center-to-center
- Avoid placing under tall components
- Keep away from board edges (>3mm clearance)
- Arrange in regular grid when possible (easier alignment)

**Net Assignment:**
- Assign test points to same net as critical signals
- Power, ground, and key signal nodes
- Connector pins (if testing from opposite side)

### Fixture Design

**Spring Force Balance:**
- Total closing force = Number of pins × Force per pin
- Aim for <500g total (comfortable to close by hand)
- For 100 pins at 50g each = 5kg (too much!)
- Solution: Use lower-force probe, or selective testing

**Alignment Features:**
- Use dowel pins or alignment bosses
- Critical for fixtures with >50 test points
- Prevents PCB shifting during testing
- Reduces probe tip wear

**Hinge Design:**
- Position hinge opposite from probe concentration
- Use stainless steel washers for smooth operation
- Add handle or finger tab for easy opening
- Consider gas spring for assisted opening (large fixtures)

### Testing Strategy

**Selective Testing:**
- Not every pad needs a probe
- Focus on critical signals: Power, ground, clock, data
- Use boundary scan or other methods for dense areas
- Reduces probe count and closing force

**Test Sequence:**
- Power continuity first (prevent shorts)
- Ground continuity
- Signal connections
- Programming/boundary scan if applicable

**Pass/Fail Criteria:**
- Define maximum contact resistance (typically 10-50Ω)
- Set timeout for probe contact (pogo pins may bounce)
- Use 4-wire measurement for accurate resistance reading

---

## ❓ FAQ

### Q: Can I mix different pogo pin models in one fixture?

**A:** Yes, but not recommended. Different spring forces will cause uneven contact and difficulty closing. If necessary, group high-force pins together and add mechanical advantage (lever, cam, etc.).

### Q: How do I clean pogo pins?

**A:** Wipe tips with lint-free cloth dampened with isopropyl alcohol (IPA). For stubborn oxidation, use a contact cleaner spray. Do not use abrasive materials (damages gold plating).

### Q: My pogo pins are sticking or not returning smoothly.

**A:** Common causes:
1. Debris in receptacle - blow out with compressed air
2. Damaged spring - replace probe pin
3. Corrosion - clean with contact cleaner or replace
4. Over-compression - check fixture stack-up calculation

### Q: Can I use pogo pins for power delivery?

**A:** Yes, but carefully:
- P75 series: Max 1.5A per pin (use multiple pins in parallel for higher current)
- Fixtest 100: 3A continuous per pin
- Calculate voltage drop: V = I × R (where R = contact resistance)
- Always use separate sense pins for 4-wire measurement

### Q: How do I know when to replace probe pins?

**A:** Replace when:
- Reached 50-75% of rated cycle life
- Contact resistance >100mΩ (2× new spec)
- Visible tip damage
- Intermittent connections
- Don't wait for complete failure!

### Q: What's the difference between receptacle and probe pin?

**A:** 
- **Receptacle** (holder): Permanent part installed in fixture plate, holds the probe
- **Probe pin** (plunger): Spring-loaded wear component, inserts into receptacle
- Think of it like a battery holder (receptacle) and battery (probe pin)

### Q: Why do I have test failures on known-good boards?

**A:** Check:
1. Probe alignment - use track.dxf overlay to verify
2. Compression - may be too light, increase clamping pressure
3. Dirty probes - clean with IPA
4. PCB warpage - fixture may not compensate for bow
5. Probe wear - replace old pins

### Q: Can OpenFixture work with other pogo pin brands?

**A:** Absolutely! Just set `pogo_uncompressed_length_mm` in config to match your probe. The hole diameter may need adjustment in the OpenSCAD file (default 0.75mm radius = 1.5mm diameter for P75 series).

---

## 🌐 Additional Resources

**OpenFixture Documentation:**
- [README.md](README.md) - Main project documentation
- [fixture_config.toml](fixture_config.toml) - Configuration with pogo pin examples
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Upgrade guide

**Datasheets:**
- [Digole P75 Series](https://www.digole.com/index.php?categoryID=115)
- [TME Fixtest Series 100](https://www.tme.eu/pl/details/s100.00-l/igly-testowe/fixtest/s-100-00-l/)

**Further Reading:**
- Test probe theory: [Spring Probe Fundamentals](https://www.mill-max.com/technical-resources)
- Contact physics: IEC 61076-4-114 (Pogo pin test methods)
- Fixture design: IPC-TM-650 (Test methods for PCB testing)

---

**Document Version**: 1.0  
**Last Updated**: February 18, 2026  
**Maintainer**: OpenFixture Project Contributors  
**License**: CC BY-SA 4.0
