import socket
import threading
import flet as ft

def main(page: ft.Page):
    page.title = "SCADA Remote Control"
    page.bgcolor = "#F8FAFC"  
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO  

    # Initialize client network socket
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_client.bind(("0.0.0.0", 61235))
    except Exception as e:
        print(f"Socket bind warning: {e}")

    # --- STATUS INDICATOR WIDGETS ---
    status_dot = ft.Container(
        width=12,
        height=12,
        bgcolor=ft.Colors.BLUE_GREY_300,
        border_radius=6
    )
    status_text = ft.Text("UNKNOWN (WAITING FOR CLICK)", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_GREY_700)

    def listen_for_pc():
        while True:
            try:
                data, _ = udp_client.recvfrom(1024)
                message = data.decode('utf-8')
                
                if message == "STATUS_GREEN":
                    status_dot.bgcolor = ft.Colors.GREEN_500
                    status_text.value = "MOTOR ON"
                elif message == "STATUS_GRAY":
                    status_dot.bgcolor = ft.Colors.BLUE_GREY_400
                    status_text.value = "MOTOR OFF"
                
                page.update()
            except:
                break

    threading.Thread(target=listen_for_pc, daemon=True).start()

    # --- INPUT FIELDS ---
    ip_input = ft.TextField(
        label="SCADA Server IP", value="10.201.205.60", prefix_icon=ft.Icons.WIFI,
        border_radius=10, border_color=ft.Colors.BLUE_GREY_200, focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER, height=55
    )
    port_input = ft.TextField(
        label="Server Port", value="61234", prefix_icon=ft.Icons.SETTINGS_ETHERNET,
        border_radius=10, border_color=ft.Colors.BLUE_GREY_200, focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER, height=55
    )
    x_input = ft.TextField(
        label="Target X Coord", value="1000", prefix_icon=ft.Icons.SUBDIRECTORY_ARROW_RIGHT,
        border_radius=10, border_color=ft.Colors.BLUE_GREY_200, focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER, height=55, expand=True
    )
    y_input = ft.TextField(
        label="Target Y Coord", value="500", prefix_icon=ft.Icons.SOUTH_EAST,
        border_radius=10, border_color=ft.Colors.BLUE_GREY_200, focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER, height=55, expand=True
    )

    def trigger_feeding(e):
        try:
            status_dot.bgcolor = ft.Colors.AMBER_500
            status_text.value = "CHECKING HMI PIXEL STATUS..."
            page.update()

            target_ip = ip_input.value.strip()
            target_port = int(port_input.value.strip())
            payload = f"start_motor:{x_input.value.strip()}:{y_input.value.strip()}"
            udp_client.sendto(payload.encode('utf-8'), (target_ip, target_port))
        except Exception as err:
            print(f"Network error: {err}")

    # --- CARD LAYOUTS ---
    status_card = ft.Container(
        content=ft.Column([
            ft.Text("SYSTEM FEEDBACK", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ft.Row([status_dot, status_text], spacing=10)
        ]),
        padding=15, bgcolor=ft.Colors.WHITE, border_radius=15, shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    network_card = ft.Container(
        content=ft.Column([
            ft.Text("NETWORK CONFIGURATION", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ip_input, port_input
        ], spacing=15),
        padding=20, bgcolor=ft.Colors.WHITE, border_radius=15, shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    coordinates_card = ft.Container(
        content=ft.Column([
            ft.Text("SCADA CLICK TARGETS", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ft.Row([x_input, y_input], spacing=10)
        ], spacing=15),
        padding=20, bgcolor=ft.Colors.WHITE, border_radius=15, shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    # --- VISUAL ASSET DESIGNATED FOR INSIDE CONTROL CARD ---
    bigbag_image = ft.Image(
        src="bigbag.png",
        height=160,          # Sized down slightly so everything fits comfortably together
        fit="contain"
    )

    feeding_button = ft.FilledButton(
        "BIGBAG FEEDING", icon=ft.Icons.PLAY_ARROW_ROUNDED,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, padding=20, shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=trigger_feeding, expand=True, height=65
    )

    # Process Card Wrapper (Updated: Stacks Image neatly above the button row)
    control_card = ft.Container(
        content=ft.Column([
            ft.Text("PROCESS CONTROL", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ft.Row([bigbag_image], alignment=ft.MainAxisAlignment.CENTER), # Image placed above
            ft.Row([feeding_button], alignment=ft.MainAxisAlignment.CENTER) # Button row immediately below
        ], spacing=15),
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    # --- Assemble Layout Vertically ---
    page.add(
        ft.Column([
            ft.Container(height=5),
            status_card,
            network_card,
            coordinates_card,
            control_card
        ], spacing=15, alignment=ft.MainAxisAlignment.START)
    )

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
