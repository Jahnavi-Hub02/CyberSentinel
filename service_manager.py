#!/usr/bin/env python
"""
CyberSentinel Service Manager
Manages backend and frontend services with clean startup and shutdown
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
BACKEND_PORT = 8000
FRONTEND_PORT = 8501

class ServiceManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        
    def cleanup_ports(self):
        """Kill any existing processes on our ports"""
        print("🧹 Cleaning up ports...")
        
        # Windows-specific cleanup
        if os.name == 'nt':  # Windows
            for port in [BACKEND_PORT, FRONTEND_PORT]:
                try:
                    import subprocess
                    result = subprocess.run(
                        f'netstat -ano | findstr ":{port}"',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        for line in result.stdout.split('\n'):
                            parts = line.split()
                            if parts:
                                try:
                                    pid = parts[-1]
                                    subprocess.run(f'taskkill /PID {pid} /F', shell=True, 
                                                capture_output=True)
                                    print(f"  ✅ Killed process on port {port}")
                                except:
                                    pass
                except:
                    pass
        
        time.sleep(2)
        print("  ✅ Ports cleaned\n")
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🚀 Starting Backend API (port 8000)...")
        try:
            # Set working directory to project root
            os.chdir(PROJECT_ROOT)
            
            cmd = [
                sys.executable, "-m", "uvicorn",
                "backend.app:app",
                "--host", "127.0.0.1",
                "--port", str(BACKEND_PORT),
                "--log-level", "warning"
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print(f"  ✅ Backend running on http://127.0.0.1:{BACKEND_PORT}\n")
                return True
            else:
                print(f"  ❌ Backend failed to start\n")
                return False
                
        except Exception as e:
            print(f"  ❌ Error starting backend: {e}\n")
            return False
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        print("🎨 Starting Frontend Dashboard (port 8501)...")
        try:
            os.chdir(PROJECT_ROOT)
            
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                "frontend/app.py",
                "--server.port", str(FRONTEND_PORT),
                "--logger.level", "error",
                "--client.showErrorDetails", "false"
            ]
            
            self.frontend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print(f"  ✅ Frontend running on http://localhost:{FRONTEND_PORT}\n")
                return True
            else:
                print(f"  ❌ Frontend failed to start\n")
                return False
                
        except Exception as e:
            print(f"  ❌ Error starting frontend: {e}\n")
            return False
    
    def start_all(self):
        """Start all services"""
        print("\n" + "="*80)
        print("  🚀 CYBERSENTIAL - SERVICE STARTUP")
        print("="*80 + "\n")
        
        self.cleanup_ports()
        
        backend_ok = self.start_backend()
        frontend_ok = self.start_frontend()
        
        if backend_ok and frontend_ok:
            self.show_status()
            return True
        else:
            return False
    
    def show_status(self):
        """Show current service status"""
        print("="*80)
        print("  ✅ ALL SERVICES RUNNING")
        print("="*80)
        print("""
🔵 BACKEND API
   📍 http://127.0.0.1:8000
   📚 Docs: http://127.0.0.1:8000/docs
   
🎨 FRONTEND DASHBOARD
   📍 http://localhost:8501
   
💡 NEXT STEPS:
   1. Open: http://localhost:8501
   2. Explore the dashboard
   3. (Optional) see `docs/ML_DETECTION_GUIDE.md` for demo instructions
   
⚠️  Keep this terminal open! Services run while terminal is open.
   Press CTRL+C to stop all services.

""" + "="*80)
    
    def stop_all(self):
        """Stop all services gracefully"""
        print("\n⏹️  Stopping services...\n")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                self.backend_process.kill()
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except:
                self.frontend_process.kill()
        
        print("✅ All services stopped\n")
    
    def run(self):
        """Run services and keep them alive"""
        if not self.start_all():
            print("❌ Failed to start services\n")
            sys.exit(1)
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
                # Check if either process died unexpectedly
                if self.backend_process and self.backend_process.poll() is not None:
                    print("⚠️  Backend process died unexpectedly!")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("⚠️  Frontend process died unexpectedly!")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n⏹️  Shutting down services...")
            self.stop_all()
            print("✅ Goodbye!\n")
            sys.exit(0)

def main():
    # Backwards-compatible wrapper - delegates to scripts/service_manager.py
    try:
        from scripts.service_manager import main as scripts_main
        scripts_main()
    except Exception as e:
        print(f"Error: could not run scripts/service_manager: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
