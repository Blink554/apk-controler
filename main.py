import socket
import flet as ft

def main(page: ft.Page):
    # Minimal mobile page configuration
    page.title = "SCADA Remote"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # IP of your Windows PC running the server and its port
    TARGET_IP = "10.201.205.60"
    TARGET_PORT = 61234
    
    # Target desktop coordinates you want the mouse to jump to
    COORD_X = 500
    COORD_Y = 500

    # Initialize basic network socket
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def trigger_mouse_move(e):
        try:
            # We bundle the command and coordinates together: "start_motor:500:500"
            payload = f"start_motor:{COORD_X}:{COORD_Y}"
            udp_client.sendto(payload.encode('utf-8'), (TARGET_IP, TARGET_PORT))
            print(f"Sent signal: {payload}")
        except Exception as err:
            print(f"Network error: {err}")

    # Fixed: Passing the string text as a direct positional argument, matching Flet 0.85+
    click_button = ft.Button(
        "CLICK & MOVE MOUSE",
        icon=ft.Icons.MOUSE,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=trigger_mouse_move,
        width=250,
        height=70
    )

    page.add(click_button)

if __name__ == "__main__":
    # Fixed: Using the modern run command instead of deprecated app()
    ft.run(main)
