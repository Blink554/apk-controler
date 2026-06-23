import socket
import asyncio
import flet as ft

async def main(page: ft.Page):
    page.title = "SCADA Remote Control"
    page.bgcolor = "#F8FAFC"  
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO  

    # Internal state tracker for the BigBag counter
    bigbag_count = 0

    # Initialize client network socket
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_client.setblocking(False)  
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
    status_text = ft.Text("UNKNOWN (WAITING FOR DATA)", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_GREY_700)

    # --- COUNTER DISPLAY WIDGET ---
    counter_text = ft.Text(str(bigbag_count), size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)

    # --- FIXED: ASYNC COUNTER MECHANICS ---
    async def adjust_counter(delta):
        nonlocal bigbag_count
        bigbag_count += delta
        if bigbag_count < 0:  
            bigbag_count = 0
        counter_text.value = str(bigbag_count)
        page.update()

    # --- NATIVE ASYNC BACKGROUND LISTENER LOOP ---
    async def listen_for_pc_async():
        loop = asyncio.get_running_loop()
        while True:
            try:
                data, _ = await loop.sock_recvfrom(udp_client, 1024)
                message = data.decode('utf-8').strip()
                
                if message == "STATUS_GREEN":
                    status_dot.bgcolor = ft.Colors.GREEN_500
                    status_text.value = "MOTOR ON"
                elif message == "STATUS_GRAY":
                    status_dot.bgcolor = ft.Colors.BLUE_GREY_400
                    status_text.value = "MOTOR OFF"
                
                page.update()
                
            except Exception as e:
                print(f"Async network listener error: {e}")
                await asyncio.sleep(0.5)

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

    async def trigger_feeding(e):
        try:
            status_dot.bgcolor = ft.Colors.AMBER_500
            status_text.value = "CHECKING HMI PIXEL STATUS..."
            page.update()

            target_ip = ip_input.value.strip()
            target_port = int(port_input.value.strip())
            payload = "start_motor:trigger"
            
            loop = asyncio.get_running_loop()
            await loop.sock_sendto(udp_client, payload.encode('utf-8'), (target_ip, target_port))
        except Exception as err:
            print(f"Network click transmit error: {err}")

    # --- LAYOUT CARDS CONFIGURATION ---
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

    # FIXED: Wrapped button actions inside lambda expressions using page.run_task to handle the async math cleanly
    counter_card = ft.Container(
        content=ft.Column([
            ft.Text("BIGBAG STOCK COUNTER", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, 
                    icon_color=ft.Colors.RED_500, 
                    icon_size=36,
                    on_click=lambda e: page.run_task(adjust_counter, -1)
                ),
                ft.Container(content=counter_text, alignment=ft.Alignment(0, 0), width=100),
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE, 
                    icon_color=ft.Colors.GREEN_500, 
                    icon_size=36,
                    on_click=lambda e: page.run_task(adjust_counter, 1)
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], spacing=10),
        padding=20, bgcolor=ft.Colors.WHITE, border_radius=15, shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    bigbag_image = ft.Image(src="bigbag.png", height=160, fit="contain")

    feeding_button = ft.FilledButton(
        "BIGBAG FEEDING", icon=ft.Icons.PLAY_ARROW_ROUNDED,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, padding=20, shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=trigger_feeding, expand=True, height=65
    )

    control_card = ft.Container(
        content=ft.Column([
            ft.Text("PROCESS CONTROL", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ft.Row([bigbag_image], alignment=ft.MainAxisAlignment.CENTER), 
            ft.Row([feeding_button], alignment=ft.MainAxisAlignment.CENTER) 
        ], spacing=15),
        padding=20, bgcolor=ft.Colors.WHITE, border_radius=15, shadow=ft.BoxShadow(blur_radius=10, color="#E2E8F0")
    )

    page.add(
        ft.Column([
            ft.Container(height=5),
            status_card,
            network_card,
            counter_card,
            control_card
        ], spacing=15, alignment=ft.MainAxisAlignment.START)
    )

    page.run_task(listen_for_pc_async)

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
