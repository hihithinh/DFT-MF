import time
from datetime import datetime, timedelta
from typing import Dict, Any

class HealthService:
    """Service for application health monitoring"""
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'service': 'DFT-MF API',
            'checks': {}
        }
        
        # Check disk space
        disk_check = self._check_disk_space()
        status['checks']['disk_space'] = disk_check
        
        # Check memory usage
        memory_check = self._check_memory_usage()
        status['checks']['memory'] = memory_check
        
        # Check dependencies
        deps_check = self._check_dependencies()
        status['checks']['dependencies'] = deps_check
        
        # Check model availability
        model_check = self._check_model_availability()
        status['checks']['model'] = model_check
        
        # Determine overall status
        if any(check['status'] != 'healthy' for check in status['checks'].values()):
            status['status'] = 'unhealthy'
        
        return status
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage('/')
            free_percent = (free / total) * 100
            
            return {
                'status': 'healthy' if free_percent > 10 else 'critical',
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'free_percent': round(free_percent, 2)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            available_percent = (memory.available / memory.total) * 100
            
            return {
                'status': 'healthy' if available_percent > 20 else 'critical',
                'total_gb': round(memory.total / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'available_percent': round(available_percent, 2)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check critical dependencies"""
        dependencies = {
            'opencv': False,
            'numpy': False,
            'flask': False
        }
        
        try:
            import cv2
            dependencies['opencv'] = True
        except ImportError:
            pass
        
        try:
            import numpy as np
            dependencies['numpy'] = True
        except ImportError:
            pass
        
        try:
            import flask
            dependencies['flask'] = True
        except ImportError:
            pass
        
        all_available = all(dependencies.values())
        
        return {
            'status': 'healthy' if all_available else 'critical',
            'dependencies': dependencies
        }
    
    def _check_model_availability(self) -> Dict[str, Any]:
        """Check if ML model is available"""
        try:
            import os
            model_path = 'trained_models/CNN_CelebDF_20260325_144921_final.h5'
            
            if os.path.exists(model_path):
                return {
                    'status': 'healthy',
                    'model_path': model_path,
                    'available': True
                }
            else:
                return {
                    'status': 'warning',
                    'model_path': model_path,
                    'available': False,
                    'message': 'Model file not found, using mock predictions'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
