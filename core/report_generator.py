"""
PDF Report Generator for Green Vision AI Models
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from django.conf import settings
from django.template.loader import render_to_string


class ReportGenerator:
    """Generate PDF reports from AI model outputs"""
    
    def __init__(self):
        self.reports_dir = Path(settings.MEDIA_ROOT) / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_report(self, report_data: Dict, title: str = "Green Vision AI Models Report", include_csv: bool = False) -> Dict:
        """Generate a PDF report from model outputs"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.pdf"
            filepath = self.reports_dir / filename
            
            context = self._prepare_context(report_data, title)
            html_content = render_to_string('reports/report_template.html', context)
            pdf_path = self._generate_pdf(html_content, filepath)
            
            csv_files = []
            if include_csv:
                csv_files = self._generate_csv_files(report_data, timestamp)
            
            relative_path = f'reports/{filename}'
            report_url = f'{settings.MEDIA_URL}{relative_path}'
            file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            
            return {
                'success': True,
                'report_url': report_url,
                'filename': filename,
                'csv_files': csv_files,
                'generated_at': datetime.now().isoformat(),
                'file_size': file_size
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _prepare_context(self, report_data: Dict, title: str) -> Dict:
        """Prepare template context"""
        context = {
            'title': title,
            'generated_at': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'models': [],
            'map_snapshot': report_data.get('map_snapshot'),
            'date_range': report_data.get('date_range', {}),
        }
        
        if 'weather' in report_data and report_data['weather']:
            context['models'].append({'name': 'Weather Forecast', 'icon': 'cloud-sun', 'data': report_data['weather']})
        if 'ndvi' in report_data and report_data['ndvi']:
            context['models'].append({'name': 'NDVI Vegetation Health', 'icon': 'leaf', 'data': report_data['ndvi']})
        if 'drought' in report_data and report_data['drought']:
            context['models'].append({'name': 'Drought Prediction', 'icon': 'sun', 'data': report_data['drought']})
        if 'climate' in report_data and report_data['climate']:
            context['models'].append({'name': 'Climate Forecast', 'icon': 'cloud-sun-rain', 'data': report_data['climate']})
        
        return context
    
    def _generate_pdf(self, html_content: str, filepath: Path) -> Path:
        """Generate PDF - tries xhtml2pdf then WeasyPrint"""
        import sys
        
        # Try xhtml2pdf
        try:
            print("🔄 Attempting xhtml2pdf import...")
            import xhtml2pdf.pisa as pisa
            print("✅ xhtml2pdf imported successfully")
            
            with open(filepath, 'wb') as pdf_file:
                status = pisa.CreatePDF(html_content, dest=pdf_file)
                if not status.err:
                    print(f"✅ PDF created: {filepath}")
                    return filepath
                else:
                    print(f"⚠️ xhtml2pdf errors: {status.err}")
        except ImportError as e:
            print(f"❌ xhtml2pdf import failed: {e}")
        except Exception as e:
            print(f"❌ xhtml2pdf error: {e}")
        
        # Try WeasyPrint
        try:
            print("🔄 Attempting WeasyPrint import...")
            from weasyprint import HTML
            print("✅ WeasyPrint imported successfully")
            
            HTML(string=html_content).write_pdf(str(filepath))
            print(f"✅ PDF created: {filepath}")
            return filepath
        except ImportError as e:
            print(f"❌ WeasyPrint import failed: {e}")
        except Exception as e:
            print(f"❌ WeasyPrint error: {e}")
        
        # Fallback: Save as HTML (temporary solution)
        print("⚠️ PDF generation failed, falling back to HTML")
        html_path = filepath.with_suffix('.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report saved: {html_path}")
        
        # Return HTML path instead of raising error
        return html_path
    
    def _generate_csv_files(self, report_data: Dict, timestamp: str) -> List[str]:
        """Generate CSV files"""
        csv_files = []
        for model_name, model_data in report_data.items():
            if model_name in ['weather', 'ndvi', 'drought', 'climate'] and model_data:
                csv_filename = f"{model_name}_data_{timestamp}.csv"
                csv_path = self.reports_dir / csv_filename
                try:
                    with open(csv_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {model_name.upper()} Data\n")
                        if isinstance(model_data, dict):
                            for key, value in model_data.items():
                                if not isinstance(value, dict):
                                    f.write(f"{key},{value}\n")
                    csv_files.append(f'reports/{csv_filename}')
                except:
                    pass
        return csv_files


report_generator = ReportGenerator()
