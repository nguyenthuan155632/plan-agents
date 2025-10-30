const fs = require('fs');
const path = require('path');

// Function to generate instructions for creating PNG icons
function generateIconInstructions() {
  console.log('\n📱 PWA ICON GENERATION GUIDE\n');
  console.log('To create PNG icons from SVG, you can use one of the following methods:\n');
  
  console.log('METHOD 1: Use online tool (easiest)');
  console.log('   1. Open https://svgtopng.com/ or https://cloudconvert.com/svg-to-png');
  console.log('   2. Upload file web/public/icon.svg');
  console.log('   3. Convert and download the following sizes:');
  console.log('      - icon-192.png (192x192)');
  console.log('      - icon-512.png (512x512)');
  console.log('      - icon-180.png (180x180 - for Apple)');
  console.log('   4. Save all files to web/public/ directory\n');
  
  console.log('METHOD 2: Use ImageMagick (if installed)');
  console.log('   cd web/public');
  console.log('   convert icon.svg -resize 192x192 icon-192.png');
  console.log('   convert icon.svg -resize 512x512 icon-512.png');
  console.log('   convert icon.svg -resize 180x180 icon-180.png\n');
  
  console.log('METHOD 3: Use npm package sharp');
  console.log('   npm install sharp');
  console.log('   Then run this script again\n');
  
  // Check if sharp is available
  try {
    const sharp = require('sharp');
    console.log('✅ Sharp is installed! Generating icons...\n');
    generateIconsWithSharp(sharp);
  } catch (e) {
    console.log('⚠️  Sharp is not installed. Please choose one of the methods above.\n');
    console.log('Or run: cd web && npm install sharp && node scripts/generate-icons.js\n');
  }
}

async function generateIconsWithSharp(sharp) {
  const publicDir = path.join(__dirname, '../public');
  const svgPath = path.join(publicDir, 'icon.svg');
  
  if (!fs.existsSync(svgPath)) {
    console.error('❌ Error: icon.svg not found in public directory');
    return;
  }
  
  const sizes = [
    { name: 'icon-192.png', size: 192 },
    { name: 'icon-512.png', size: 512 },
    { name: 'icon-180.png', size: 180 },
  ];
  
  try {
    const svgBuffer = fs.readFileSync(svgPath);
    
    for (const { name, size } of sizes) {
      const outputPath = path.join(publicDir, name);
      await sharp(svgBuffer)
        .resize(size, size)
        .png()
        .toFile(outputPath);
      console.log(`✅ Generated ${name} (${size}x${size})`);
    }
    
    console.log('\n🎉 Done! All icons have been generated in web/public/\n');
  } catch (error) {
    console.error('❌ Error generating icons:', error.message);
    console.log('\n💡 Try using method 1 (online tool) instead.\n');
  }
}

generateIconInstructions();

