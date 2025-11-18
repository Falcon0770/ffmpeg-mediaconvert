#!/bin/bash
# EC2 Setup Script for FFmpeg Video Conversion (ARM64)
# Run this script once when you first SSH into your c6g.xlarge instance

echo "=================================================="
echo "FFmpeg Video Converter - EC2 ARM64 Setup"
echo "=================================================="

# Update system packages
echo "📦 Updating system packages..."
sudo yum update -y

# Install FFmpeg (ARM64 optimized)
echo "🎬 Installing FFmpeg..."
sudo yum install -y ffmpeg

# Install Python 3 and pip (usually pre-installed on Amazon Linux 2023)
echo "🐍 Installing Python 3 and pip..."
sudo yum install -y python3 python3-pip

# Install tmux for parallel processing
echo "🖥️  Installing tmux..."
sudo yum install -y tmux

# Install AWS CLI v2 (auto-detect architecture)
echo "☁️  Installing AWS CLI..."
# Remove any existing broken installation
sudo rm -rf /usr/local/aws-cli /usr/local/bin/aws /usr/local/bin/aws_completer 2>/dev/null

# Detect architecture and download correct version
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    echo "   Detected ARM64 architecture"
    curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
elif [ "$ARCH" = "x86_64" ]; then
    echo "   Detected x86_64 architecture"
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
else
    echo "   ⚠️  Unknown architecture: $ARCH"
    exit 1
fi

# Install
unzip -o awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

echo "   ✅ AWS CLI installed successfully for $ARCH"

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip3 install boto3

# Verify installations
echo ""
echo "=================================================="
echo "✅ Installation Complete! Verifying..."
echo "=================================================="

echo "FFmpeg version:"
ffmpeg -version | head -n 1

echo ""
echo "Python version:"
python3 --version

echo ""
echo "AWS CLI version:"
aws --version

echo ""
echo "tmux version:"
tmux -V

echo ""
echo "=================================================="
echo "🎉 Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Configure AWS credentials:"
echo "   aws configure"
echo ""
echo "2. Clone or upload your conversion scripts"
echo ""
echo "3. Start tmux for parallel processing:"
echo "   tmux new -s video_conversion"
echo ""
echo "4. Split into 4 panes and run the script in each"
echo "=================================================="

