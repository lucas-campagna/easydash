import dash
from dash import html, dcc, Input, State, Output, ctx, ALL
from src.components import Window
from src.config import window_default
from factory_component import Rnd, TextEditor

app = dash.Dash(__name__,assets_folder='src/assets')

app.layout = html.Div([
        html.Div(
            id='workspace',
            className='workspace'
        ),
        html.Div([
                html.Div(
                    html.Img(
                        src='/assets/img/play.png',
                        className='controllerWindowButtonsImg',
                        id='swap-dev-button-img'
                    ),
                    className='controllerWindowButtons',
                    id='swap-dev-button'
                ),
                html.Div(
                    html.Img(
                        src='/assets/img/plus.png',
                        className='controllerWindowButtonsImg',
                    ),
                    className='controllerWindowButtons',
                    id='add-window-button'
                ),
            ],
            id='dev-menu',
            className='devMenu'
        ),
        dcc.Store(id='store-selected-window-name')
    ],
    id='app',
)

@app.callback(
    Output('swap-dev-button-img','src'),
    Input('swap-dev-button','n_clicks'),
)
def swap_dev_button_children(_):
    global Window
    Window.DEV = not Window.DEV
    return '/assets/img/play.png' if Window.DEV else '/assets/img/pause.png'

@app.callback(
    Output('workspace','children'),
    Input('swap-dev-button','n_clicks'),
    Input('add-window-button','n_clicks'),
    Input('store-selected-window-name','data'),
    Input({'type':'window-close-button','index':ALL},'n_clicks'),
    prevent_initial_call=True
)
def workspace_children(btn1,btn2,selected_window_name,n_clicks):
    # print('workspace_children',ctx.triggered_id,type(ctx.triggered_id))
    # if ctx.triggered_id is None:
    #     for name, window in Window.get().items():
            # window.load()
        # return [window() for window in Window.get().values()]
    if ctx.triggered_id == 'add-window-button':
        Window.add()
    elif not type(ctx.triggered_id) == str and ctx.triggered_id['type'] == 'window-close-button':
        # print('Removing ',ctx.triggered_id['index'])
        Window.rm(ctx.triggered_id['index'])
    # print('Window.selected_window_name',Window.selected_window_name)
    if Window.selected_window_name:
        return [window() for name,window in Window.get().items() if name != Window.selected_window_name] + [Window.get(Window.selected_window_name)()]
    return [window() for window in Window.get().values()]

if __name__ == '__main__':
    app.run(debug=True)