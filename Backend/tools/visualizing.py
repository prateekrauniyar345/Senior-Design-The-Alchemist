import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from langchain.tools import tool
from datetime import datetime
from langsmith import traceable
from models.plot_visualization_model import PandasDFInput
import json
import math
import networkx as nx
import folium
from folium.plugins import HeatMap

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'

# Define directories
ROOT = Path(__file__).resolve().parents[1]
PLOTS_DIR = ROOT / "contents" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

@tool
def histogram_plot(file_path: str, plot_title: str = None) -> str:
    """
    Creates a histogram plot showing element distribution from mineral data.
    
    Args:
        file_path: Path to the JSON file containing mineral data
        plot_title: Optional custom title for the plot
        
    Returns:
        Success message with plot file path or error message
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check if 'results' key exists
        if 'results' not in data:
            return f"Error: 'results' key not found in {file_path}"
        
        # Create DataFrame from the 'results' array
        df = pd.DataFrame(data['results'])
        
        if df.empty:
            return "Error: The data file is empty."
        
        # Check if 'elements' column exists
        if 'elements' not in df.columns:
            return f"Error: 'elements' column not found in data. Available columns: {list(df.columns)}"
        
        # Flatten the list of elements and count occurrences
        all_elements = []
        for elements_list in df['elements']:
            if isinstance(elements_list, list):
                all_elements.extend(elements_list)
        
        if not all_elements:
            return "Error: No elements found in the data."
        
        # Count element frequencies
        element_counts = pd.Series(all_elements).value_counts()
        
        # Take top 20 elements
        top_elements = element_counts.head(20)
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        bars = plt.bar(range(len(top_elements)), top_elements.values, 
                      color='steelblue', edgecolor='black')
        
        # Customize the plot
        plt.xlabel('Elements', fontsize=14, fontweight='bold')
        plt.ylabel('Frequency', fontsize=14, fontweight='bold')
        
        # Set title
        if plot_title:
            plt.title(plot_title, fontsize=16, fontweight='bold', pad=20)
        else:
            plt.title('Top 20 Elements Distribution in Mineral Dataset', 
                     fontsize=16, fontweight='bold', pad=20)
        
        plt.xticks(range(len(top_elements)), top_elements.index, 
                  rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on top of bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"mineral_elements_histogram_{timestamp}.png"
        plot_path = PLOTS_DIR / plot_filename
        
        # Save the plot
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return f"Success: Histogram created and saved to {plot_path}"
        
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format in {file_path}: {str(e)}"
    except Exception as e:
        return f"Error creating histogram: {str(e)}"


@tool
def network_plot(file_path: str, top_n: int = 50, plot_title: str = None) -> str:
    """
    Creates a network visualization showing mineral relationships based on shared localities.
    Minerals are colored by Strunz classification.
    
    Args:
        file_path: Path to the JSON file containing mineral data with locality information
        top_n: Number of top minerals to include in the network (default: 50)
        plot_title: Optional custom title for the plot
        
    Returns:
        Success message with plot file path or error message
    """
    try:
        # Define Strunz color map
        color_map = {
            1: '#FF4444',  # ELEMENTS - red
            2: '#FF8C00',  # SULFIDES - orange
            3: '#FFD700',  # HALIDES - yellow
            4: '#32CD32',  # OXIDES - green
            5: '#4169E1',  # CARBONATES - blue
            6: '#4B0082',  # BORATES - indigo
            7: '#8B00FF',  # SULFATES - violet
            8: '#9932CC',  # PHOSPHATES - purple
            9: '#8B4513',  # SILICATES - brown
            10: '#808080', # ORGANIC - grey
            11: '#000000'  # Other - black
        }
        
        # Load data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if 'results' not in data:
            return f"Error: 'results' key not found in {file_path}"
        
        filtered_data = data['results'][:top_n]
        
        if not filtered_data:
            return "Error: No data available to plot"
        
        # Create graph
        G = nx.Graph()
        mineral_locality_map = {}
        
        # Build nodes and locality mapping
        for mineral in filtered_data:
            mineral_id = mineral.get('id')
            mineral_name = mineral.get('name', 'Unknown')
            localities = mineral.get('locality', [])
            
            if not mineral_id:
                continue
            
            # Get Strunz classification
            strunz_value = mineral.get('strunz10ed1', 11)
            try:
                strunz_value = int(strunz_value) if strunz_value else 11
            except (ValueError, TypeError):
                strunz_value = 11
            
            color = color_map.get(strunz_value, '#000000')
            
            # Calculate node size based on number of localities
            node_size = 300 + math.log1p(len(localities)) * 100
            
            G.add_node(mineral_id, 
                      label=mineral_name, 
                      color=color, 
                      size=node_size,
                      strunz=strunz_value)
            
            # Map localities to minerals
            for locality in localities:
                if locality not in mineral_locality_map:
                    mineral_locality_map[locality] = set()
                mineral_locality_map[locality].add(mineral_id)
        
        # Add edges between minerals sharing localities
        for locality, minerals in mineral_locality_map.items():
            minerals = list(minerals)
            for i in range(len(minerals)):
                for j in range(i + 1, len(minerals)):
                    if G.has_edge(minerals[i], minerals[j]):
                        G[minerals[i]][minerals[j]]['weight'] += 1
                    else:
                        G.add_edge(minerals[i], minerals[j], weight=1, color='#CCCCCC')
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Draw nodes
        for node in G.nodes():
            nx.draw_networkx_nodes(G, pos, 
                                 nodelist=[node],
                                 node_color=[G.nodes[node]['color']],
                                 node_size=[G.nodes[node]['size']],
                                 alpha=0.8,
                                 edgecolors='white',
                                 linewidths=2)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.3, width=1, edge_color='#CCCCCC')
        
        # Draw labels
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
        
        # Add title
        if plot_title:
            plt.title(plot_title, fontsize=18, fontweight='bold', pad=20)
        else:
            plt.title('Mineral Network - Shared Localities', fontsize=18, fontweight='bold', pad=20)
        
        # Add legend
        legend_labels = [
            '1: ELEMENTS', '2: SULFIDES', '3: HALIDES', '4: OXIDES',
            '5: CARBONATES', '6: BORATES', '7: SULFATES', 
            '8: PHOSPHATES', '9: SILICATES', '10: ORGANIC', '11: OTHER'
        ]
        legend_colors = [color_map[i] for i in range(1, 12)]
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', 
                                     markerfacecolor=color, markersize=10, 
                                     label=label) 
                         for color, label in zip(legend_colors, legend_labels)]
        plt.legend(handles=legend_handles, loc='upper left', fontsize=9, 
                  framealpha=0.9, title='Strunz Classification')
        
        plt.axis('off')
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"mineral_network_{timestamp}.png"
        plot_path = PLOTS_DIR / plot_filename
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return f"Success: Network plot created and saved to {plot_path}"
        
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format in {file_path}: {str(e)}"
    except Exception as e:
        return f"Error creating network plot: {str(e)}"


@tool
def heatmap_plot(file_path: str, plot_title: str = None) -> str:
    """
    Creates a heatmap visualization of mineral locality data on an interactive map.
    Requires locality data with latitude and longitude coordinates.
    
    Args:
        file_path: Path to the JSON file containing locality data with coordinates
        plot_title: Optional custom title for the plot
        
    Returns:
        Success message with map file path or error message
    """
    try:
        # Load data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if 'results' not in data:
            return f"Error: 'results' key not found in {file_path}"
        
        # Extract coordinates
        locations = []
        for item in data['results']:
            lat = item.get('latitude')
            lon = item.get('longitude')
            
            # Filter out invalid coordinates
            if lat and lon and lat != 0.0 and lon != 0.0:
                try:
                    locations.append([float(lat), float(lon)])
                except (ValueError, TypeError):
                    continue
        
        if not locations:
            return "Error: No valid latitude/longitude coordinates found in data"
        
        # Calculate center point
        center_lat = sum(loc[0] for loc in locations) / len(locations)
        center_lon = sum(loc[1] for loc in locations) / len(locations)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        # Add heatmap layer
        HeatMap(locations, 
               radius=15,
               blur=25,
               max_zoom=13,
               gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1.0: 'red'}
              ).add_to(m)
        
        # Add title
        if plot_title:
            title_html = f'<h3 align="center" style="font-size:20px"><b>{plot_title}</b></h3>'
        else:
            title_html = '<h3 align="center" style="font-size:20px"><b>Mineral Locality Heatmap</b></h3>'
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_filename = f"mineral_heatmap_{timestamp}.html"
        map_path = PLOTS_DIR / map_filename
        m.save(str(map_path))
        
        return f"Success: Heatmap created and saved to {map_path}"
        
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format in {file_path}: {str(e)}"
    except Exception as e:
        return f"Error creating heatmap: {str(e)}"