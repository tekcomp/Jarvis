#!/usr/bin/env python3
"""
JARVIS AI Voice Assistant - Unified Entry Point
Platform detection and command-line routing
"""

import sys
import os
import argparse
import platform
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/jarvis.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class JarvisLauncher:
    """Main launcher class with platform detection"""
    
    def __init__(self):
        self.platform = platform.system()
        self.script_dir = Path(__file__).parent
        self.supported_platforms = ['Windows', 'Linux', 'Darwin']
    
    def detect_platform(self):
        """Detect current platform"""
        if self.platform not in self.supported_platforms:
            logger.warning(f"Unsupported platform: {self.platform}")
            logger.warning(f"Supported platforms: {', '.join(self.supported_platforms)}")
        
        return self.platform
    
    def check_dependencies(self):
        """Check required dependencies"""
        required_modules = [
            'requests',
            'yaml',
            'sounddevice',
            'numpy'
        ]
        
        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            logger.error(f"Missing required dependencies: {', '.join(missing)}")
            logger.info("Run setup.bat or 'pip install -r requirements.txt' to install dependencies")
            return False
        
        logger.info("All dependencies satisfied")
        return True
    
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            if response.status_code == 200:
                logger.info("Ollama API is responding")
                return True
        except Exception as e:
            logger.warning(f"Ollama API not responding: {e}")
            return False
    
    def launch_windows_batch(self, script_name):
        """Launch Windows batch file"""
        script_path = self.script_dir / "scripts" / script_name
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return False
        
        logger.info(f"Launching {script_name}")
        os.system(f"start cmd /c \"{script_path}\"")
        return True
    
    def launch_powershell(self, script_name):
        """Launch PowerShell script"""
        script_path = self.script_dir / "scripts" / script_name
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return False
        
        logger.info(f"Launching {script_name}")
        os.system(f"powershell -NoProfile -ExecutionPolicy Bypass -File \"{script_path}\"")
        return True
    
    def launch_python_module(self, module_path):
        """Direct Python execution"""
        if not os.path.exists(module_path):
            logger.error(f"Module not found: {module_path}")
            return False
        
        logger.info(f"Executing: {module_path}")
        os.system(f"python \"{module_path}\"")
        return True
    
    def parse_arguments(self):
        """Parse command-line arguments"""
        parser = argparse.ArgumentParser(
            description="JARVIS AI Voice Assistant",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py                    # Launch with default settings
  python main.py --debug            # Run with debug logging
  python main.py --no-warmup        # Skip model warmup
  python main.py --model gemma3     # Specify model
  python main.py --monitor          # Start health dashboard
  python main.py --test-boot        # Run boot sequence tests
  python main.py --install-models   # Auto-download recommended models
            """
        )
        
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging"
        )
        
        parser.add_argument(
            "--no-warmup",
            action="store_true",
            help="Skip model warmup during boot"
        )
        
        parser.add_argument(
            "--model",
            type=str,
            default="auto",
            help="Specify model to use (default: auto-select)"
        )
        
        parser.add_argument(
            "--monitor",
            action="store_true",
            help="Start health monitoring dashboard"
        )
        
        parser.add_argument(
            "--test-boot",
            action="store_true",
            help="Run boot sequence tests"
        )
        
        parser.add_argument(
            "--install-models",
            action="store_true",
            help="Auto-download recommended models"
        )
        
        parser.add_argument(
            "--config",
            type=str,
            default="config/jarvis_config.json",
            help="Path to configuration file (default: config/jarvis_config.json)"
        )
        
        return parser.parse_args()
    
    def run(self, args):
        """Main execution logic"""
        logger.info("=" * 50)
        logger.info("JARVIS AI - Unified Entry Point")
        logger.info("=" * 50)
        logger.info(f"Platform: {self.detect_platform()}")
        logger.info(f"Python version: {sys.version}")
        
        # Setup logging level
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        
        # Handle special commands
        if args.install_models:
            logger.info("Installing recommended models...")
            self._install_models()
            return
        
        if args.monitor:
            logger.info("Starting health dashboard...")
            self._start_monitor()
            return
        
        if args.test_boot:
            logger.info("Running boot sequence tests...")
            self._run_boot_tests()
            return
        
        # Normal startup
        logger.info("Starting Jarvis voice assistant...")
        
        # Check dependencies
        if not self.check_dependencies():
            sys.exit(1)
        
        # Check Ollama
        if not self.check_ollama():
            logger.warning("Ollama is not running. Please start it first.")
            logger.info("Start Ollama with: ollama serve")
            logger.info("Then run: python main.py")
            sys.exit(1)
        
        # Launch appropriate launcher
        self._launch_jarvis(args)
    
    def _install_models(self):
        """Install recommended models"""
        try:
            import subprocess
            
            models = ['gemma3', 'llama3.1']
            for model in models:
                logger.info(f"Installing {model}...")
                result = subprocess.run(
                    ['ollama', 'pull', model],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    logger.info(f"✓ {model} installed successfully")
                else:
                    logger.error(f"✗ Failed to install {model}")
        except Exception as e:
            logger.error(f"Error installing models: {e}")
    
    def _start_monitor(self):
        """Start health monitoring dashboard"""
        try:
            from monitor import app
            app.run(host='0.0.0.0', port=8050, debug=False, use_reloader=False)
        except ImportError:
            logger.error("Dashboard module not found. Install dependencies first.")
            sys.exit(1)
    
    def _run_boot_tests(self):
        """Run boot sequence tests"""
        try:
            from tests.test_boot import run_all_boot_tests
            result = run_all_boot_tests()
            if result['passed'] >= result['total'] * 0.8:
                logger.info("Boot tests passed!")
            else:
                logger.warning(f"Boot tests: {result['passed']}/{result['total']} passed")
        except ImportError:
            logger.error("Boot tests module not found. Install dependencies first.")
            sys.exit(1)
    
    def _launch_jarvis(self, args):
        """Launch Jarvis based on platform and arguments"""
        
        # Windows specific launchers
        if self.platform == 'Windows':
            if args.model != 'auto':
                # Custom model launch via PowerShell
                script = self.script_dir / "scripts" / "Start_jarvis_optimized.ps1"
                if script.exists():
                    cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{script}" -Model "{args.model}"'
                    os.system(cmd)
                    return
            
            # Default: Use optimized boot script
            script_name = "Start_jarvis_optimized.bat"
            if args.no_warmup:
                script_name = "Start_jarvis.bat"
            
            self.launch_windows_batch(script_name)
        
        # Linux/macOS support (for future expansion)
        elif self.platform in ['Linux', 'Darwin']:
            script_name = "Start_jarvis_optimized.sh"
            if os.path.exists(self.script_dir / "scripts" / script_name):
                self.launch_powershell(script_name)
            else:
                # Fallback to Python module
                self.launch_python_module(str(self.script_dir / "jarvis.py"))
        
        else:
            # Fallback to Python module
            self.launch_python_module(str(self.script_dir / "jarvis.py"))


def main():
    """Main entry point"""
    launcher = JarvisLauncher()
    args = launcher.parse_arguments()
    launcher.run(args)


if __name__ == "__main__":
    main()