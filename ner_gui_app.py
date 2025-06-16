#!/usr/bin/env python3
"""
Italian Medical NER - GUI Application
A user-friendly desktop application for Italian medical entity recognition
Created by: NinoF840
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
from datetime import datetime
import os
import sys

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from improved_inference import ImprovedItalianMedicalNER
except ImportError:
    # Fallback if improved_inference is not available
    print("Warning: Enhanced inference not available. Using basic functionality.")
    ImprovedItalianMedicalNER = None

class ItalianMedicalNERApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Italian Medical NER - Enhanced by NinoF840")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Initialize NER model
        self.ner_model = None
        self.model_loaded = False
        
        # Create GUI
        self.create_widgets()
        self.load_model_async()
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Italian Medical NER - Enhanced Edition", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Text", padding="5")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, wrap=tk.WORD)
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Sample text button
        sample_btn = ttk.Button(input_frame, text="Load Sample Text", command=self.load_sample_text)
        sample_btn.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.analyze_btn = ttk.Button(control_frame, text="Analyze Text", 
                                     command=self.analyze_text, state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(control_frame, text="Clear All", command=self.clear_all)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(control_frame, text="Save Results", 
                                  command=self.save_results, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(control_frame, text="Settings", padding="5")
        settings_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(settings_frame, text="Confidence:").grid(row=0, column=0, padx=5)
        self.confidence_var = tk.DoubleVar(value=0.6)
        confidence_spin = ttk.Spinbox(settings_frame, from_=0.1, to=1.0, increment=0.1, 
                                     width=8, textvariable=self.confidence_var)
        confidence_spin.grid(row=0, column=1, padx=5)
        
        self.enhancement_var = tk.BooleanVar(value=True)
        enhancement_check = ttk.Checkbutton(settings_frame, text="Enhanced Detection", 
                                          variable=self.enhancement_var)
        enhancement_check.grid(row=0, column=2, padx=10)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="5")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create notebook for results tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Entities tab
        entities_frame = ttk.Frame(self.notebook)
        self.notebook.add(entities_frame, text="Entities")
        
        # Create treeview for entities
        columns = ('Text', 'Type', 'Confidence', 'Source')
        self.entities_tree = ttk.Treeview(entities_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.entities_tree.heading(col, text=col)
            self.entities_tree.column(col, width=150)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(entities_frame, orient=tk.VERTICAL, command=self.entities_tree.yview)
        h_scrollbar = ttk.Scrollbar(entities_frame, orient=tk.HORIZONTAL, command=self.entities_tree.xview)
        self.entities_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.entities_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        entities_frame.columnconfigure(0, weight=1)
        entities_frame.rowconfigure(0, weight=1)
        
        # Statistics tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=8, wrap=tk.WORD)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Initializing model...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Store last results for saving
        self.last_results = None
    
    def load_model_async(self):
        """Load the NER model in a separate thread"""
        def load_model():
            try:
                self.status_var.set("Loading model...")
                if ImprovedItalianMedicalNER:
                    self.ner_model = ImprovedItalianMedicalNER(
                        confidence_threshold=self.confidence_var.get()
                    )
                    self.model_loaded = True
                    self.root.after(0, self.on_model_loaded)
                else:
                    self.root.after(0, self.on_model_load_failed)
            except Exception as e:
                self.root.after(0, lambda: self.on_model_load_failed(str(e)))
        
        thread = threading.Thread(target=load_model, daemon=True)
        thread.start()
    
    def on_model_loaded(self):
        """Called when model is successfully loaded"""
        self.status_var.set("Model loaded successfully. Ready for analysis.")
        self.analyze_btn.config(state=tk.NORMAL)
    
    def on_model_load_failed(self, error=None):
        """Called when model loading fails"""
        error_msg = f"Model loading failed: {error}" if error else "Model loading failed. Using basic mode."
        self.status_var.set(error_msg)
        messagebox.showwarning("Model Loading", error_msg)
        # Enable basic functionality
        self.analyze_btn.config(state=tk.NORMAL)
    
    def load_sample_text(self):
        """Load sample Italian medical text"""
        sample_texts = [
            "Il paziente ha lamentato forti mal di testa e nausea che persistevano da due giorni.",
            "Per alleviare i sintomi, gli è stato prescritto il paracetamolo e riposo.",
            "È necessario eseguire un esame del sangue e una radiografia del torace.",
            "La terapia antibiotica è stata efficace nel trattamento dell'infezione.",
            "Il diabete del paziente è controllato con insulina e dieta appropriata.",
            "La gastroscopia ha rivelato un'ulcera gastrica che richiede trattamento medico."
        ]
        
        sample_text = "\n\n".join(sample_texts)
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, sample_text)
    
    def analyze_text(self):
        """Analyze the input text for medical entities"""
        text = self.input_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Input Required", "Please enter some text to analyze.")
            return
        
        # Disable analyze button during processing
        self.analyze_btn.config(state=tk.DISABLED)
        self.status_var.set("Analyzing text...")
        
        def analyze():
            try:
                if self.model_loaded and self.ner_model:
                    # Update model confidence threshold
                    self.ner_model.confidence_threshold = self.confidence_var.get()
                    
                    # Analyze text
                    result = self.ner_model.predict(text, apply_enhancement=self.enhancement_var.get())
                    self.root.after(0, lambda: self.display_results(result))
                else:
                    # Basic fallback analysis
                    basic_result = self.basic_analysis(text)
                    self.root.after(0, lambda: self.display_results(basic_result))
            except Exception as e:
                self.root.after(0, lambda: self.on_analysis_error(str(e)))
        
        thread = threading.Thread(target=analyze, daemon=True)
        thread.start()
    
    def basic_analysis(self, text):
        """Basic analysis when full model is not available"""
        import re
        
        # Simple pattern matching for demonstration
        patterns = {
            'PROBLEM': [
                r'\b(mal di testa|cefalea|emicrania|dolore|febbre|nausea|tosse|diabete|ulcera)\b',
                r'\b(infezione|allergia|tumore|ipertensione|ipotensione)\b'
            ],
            'TREATMENT': [
                r'\b(paracetamolo|aspirina|antibiotico|insulina|terapia|trattamento)\b',
                r'\b(farmaco|medicina|cortisone|fisioterapia)\b'
            ],
            'TEST': [
                r'\b(esame|radiografia|ecografia|test|analisi|biopsia|gastroscopia)\b',
                r'\b(elettrocardiogramma|spirometria|mammografia)\b'
            ]
        }
        
        entities = []
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'label': entity_type,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8,
                        'source': 'pattern'
                    })
        
        return {
            'text': text,
            'entities': entities,
            'total_entities': len(entities),
            'entity_counts': {entity_type: sum(1 for e in entities if e['label'] == entity_type) 
                            for entity_type in ['PROBLEM', 'TREATMENT', 'TEST']}
        }
    
    def display_results(self, result):
        """Display analysis results in the GUI"""
        # Clear previous results
        for item in self.entities_tree.get_children():
            self.entities_tree.delete(item)
        
        # Display entities
        for entity in result['entities']:
            source_icon = "🤖" if entity['source'] == 'model' else "📝" if entity['source'] == 'pattern' else "📚"
            self.entities_tree.insert('', tk.END, values=(
                entity['text'],
                entity['label'],
                f"{entity['confidence']:.3f}",
                f"{source_icon} {entity['source']}"
            ))
        
        # Display statistics
        stats = self.generate_statistics(result)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        
        # Update status
        self.status_var.set(f"Analysis complete. Found {result['total_entities']} entities.")
        
        # Re-enable buttons
        self.analyze_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        
        # Store results for saving
        self.last_results = result
    
    def generate_statistics(self, result):
        """Generate statistics text from results"""
        stats = []
        stats.append("=== ANALYSIS STATISTICS ===")
        stats.append(f"Total entities found: {result['total_entities']}")
        stats.append("")
        
        if 'entity_counts' in result:
            stats.append("Entity distribution:")
            for entity_type, count in result['entity_counts'].items():
                if count > 0:
                    stats.append(f"  {entity_type}: {count} entities")
            stats.append("")
        
        if result['entities']:
            # Calculate confidence statistics
            confidences = [e['confidence'] for e in result['entities']]
            avg_confidence = sum(confidences) / len(confidences)
            min_confidence = min(confidences)
            max_confidence = max(confidences)
            
            stats.append("Confidence statistics:")
            stats.append(f"  Average: {avg_confidence:.3f}")
            stats.append(f"  Minimum: {min_confidence:.3f}")
            stats.append(f"  Maximum: {max_confidence:.3f}")
            stats.append("")
            
            # Source distribution
            source_counts = {}
            for entity in result['entities']:
                source = entity['source']
                source_counts[source] = source_counts.get(source, 0) + 1
            
            stats.append("Detection sources:")
            for source, count in source_counts.items():
                icon = "🤖" if source == 'model' else "📝" if source == 'pattern' else "📚"
                stats.append(f"  {icon} {source}: {count} entities")
        
        stats.append("")
        stats.append("=== ENTITY DETAILS ===")
        for i, entity in enumerate(result['entities'], 1):
            source_icon = "🤖" if entity['source'] == 'model' else "📝" if entity['source'] == 'pattern' else "📚"
            stats.append(f"{i}. {entity['text']} ({entity['label']})")
            stats.append(f"   Confidence: {entity['confidence']:.3f} | Source: {source_icon} {entity['source']}")
        
        return "\n".join(stats)
    
    def on_analysis_error(self, error):
        """Handle analysis errors"""
        self.status_var.set(f"Analysis failed: {error}")
        messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n{error}")
        self.analyze_btn.config(state=tk.NORMAL)
    
    def clear_all(self):
        """Clear all input and results"""
        self.input_text.delete(1.0, tk.END)
        for item in self.entities_tree.get_children():
            self.entities_tree.delete(item)
        self.stats_text.delete(1.0, tk.END)
        self.status_var.set("Ready for analysis.")
        self.save_btn.config(state=tk.DISABLED)
        self.last_results = None
    
    def save_results(self):
        """Save analysis results to file"""
        if not self.last_results:
            messagebox.showwarning("No Results", "No analysis results to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Analysis Results"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    # Save as JSON
                    save_data = {
                        'timestamp': datetime.now().isoformat(),
                        'model_info': 'Italian Medical NER - Enhanced by NinoF840',
                        'settings': {
                            'confidence_threshold': self.confidence_var.get(),
                            'enhancement_enabled': self.enhancement_var.get()
                        },
                        'results': self.last_results
                    }
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, indent=2, ensure_ascii=False)
                else:
                    # Save as text
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("Italian Medical NER - Analysis Results\n")
                        f.write("=" * 40 + "\n\n")
                        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Text analyzed: {self.last_results['text'][:100]}...\n\n")
                        f.write(self.generate_statistics(self.last_results))
                
                messagebox.showinfo("Save Successful", f"Results saved to {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save results:\n{str(e)}")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ItalianMedicalNERApp(root)
    
    # Set window icon (if available)
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass  # Icon file not found, continue without icon
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()

