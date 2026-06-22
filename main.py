import socket
import flet as ft

def main(page: ft.Page):
    # Responsive mobile page configurations
    page.title = "SCADA Remote Control"
    page.bgcolor = "#F8FAFC"  # Clean, modern light-gray background
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO  # Protects smaller screens with smooth vertical scrolling

    # Initialize client network socket
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # --- INPUT FIELDS WITH INDUSTRIAL STYLING ---
    ip_input = ft.TextField(
        label="SCADA Server IP", 
        value="10.201.205.60", 
        prefix_icon=ft.Icons.WIFI,
        border_radius=10,
        border_color=ft.Colors.BLUE_GREY_200,
        focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER,
        height=55
    )
    
    port_input = ft.TextField(
        label="Server Port", 
        value="61234", 
        prefix_icon=ft.Icons.SETTINGS_ETHERNET,
        border_radius=10,
        border_color=ft.Colors.BLUE_GREY_200,
        focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER,
        height=55
    )

    x_input = ft.TextField(
        label="Target X Coord", 
        value="500", 
        prefix_icon=ft.Icons.SUBDIRECTORY_ARROW_RIGHT,
        border_radius=10,
        border_color=ft.Colors.BLUE_GREY_200,
        focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER,
        height=55,
        expand=True  # Automatically takes up exactly half the Row width
    )
    
    y_input = ft.TextField(
        label="Target Y Coord", 
        value="500", 
        prefix_icon=ft.Icons.SOUTH_EAST,
        border_radius=10,
        border_color=ft.Colors.BLUE_GREY_200,
        focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER,
        height=55,
        expand=True  # Automatically takes up exactly half the Row width
    )

    # --- NETWORK EXECUTION ---
    def trigger_feeding(e):
        try:
            target_ip = ip_input.value.strip()
            target_port = int(port_input.value.strip())
            coord_x = x_input.value.strip()
            coord_y = y_input.value.strip()

            # Package data dynamically based on screen inputs
            payload = f"start_motor:{coord_x}:{coord_y}"
            udp_client.sendto(payload.encode('utf-8'), (target_ip, target_port))
            print(f"Dispatched: {payload} to {target_ip}:{target_port}")
        except Exception as err:
            print(f"Network error: {err}")

    # --- STRUCTURED CARD SECTIONS ---
    # Connection Parameters Card
    network_card = ft.Container(
        content=ft.Column([
            ft.Text("NETWORK CONFIGURATION", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ip_input,
            port_input
        ], spacing=15),
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    # Mouse Position Parameters Card
    coordinates_card = ft.Container(
        content=ft.Column([
            ft.Text("SCADA CLICK TARGETS", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ft.Row([
                x_input,
                y_input,
            ], spacing=10)
        ], spacing=15),
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    # Main Action Call Button (Optimized with FilledButton for width stretching)
    feeding_button = ft.FilledButton(
        "BIGBAG FEEDING",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=trigger_feeding,
        expand=True,  # Makes the button grow to fill the container width
        height=65
    )

    # Process Card Wrapper
    control_card = ft.Container(
        content=ft.Column([
            ft.Text("PROCESS CONTROL", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ft.Row([feeding_button], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=15),
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    # --- Assemble Layout Vertically ---
    page.add(
        ft.Column([
            ft.Container(height=10),  # Top breathing spacer
            network_card,
            coordinates_card,
            control_card
        ], spacing=20, alignment=ft.MainAxisAlignment.START)
    )

if __name__ == "__main__":
    ft.run(main)
