from factory_component import Rnd, TextEditor
from config import window_default,dragGrid, resizeGrid
from dash import dcc, html, Input, Output, callback, MATCH, ctx
import dash

def WinDev(*args,**kwargs):
    return html.Div([
            html.Div([
                    html.Div(className='windowHeaderButton windowCloseButton'),
                    html.Div(className='windowHeaderButton windowMaximizeButton'),
                    html.Div(className='windowHeaderButton windowMinimizeButton'),
                ],
                className='windowHeader'
            ),
            TextEditor(*args,**kwargs,className='windowTextEditor'),
        ],
        className='windowHandle'
    )
def WinError(*args,**kwargs):
    return html.Div([
            html.Div(*args,**kwargs,className='windowDebugError'),
        ],
        className='windowHandle'
    )

class Window:
    __windows = {}

    def __init__(self,name:str='',code:str=''):
        self.__name = name or f'Window {len(Window.__windows)+1}'
        self.__code = code
        self.error = ''
        self.__layout = ''
        self.position = dict(x=window_default['x'],y=window_default['y'])
        self.size = dict(width=window_default['width'],height=window_default['height'])
        self.__build()

    def __call__(self,**kwargs):
        code = kwargs.get('code','')
        dev = kwargs.get('dev',True)
        if code and code != self.__code:
            self.__code = code
            self.__build()
        return Rnd(
            # WinError('self.error'),
            children=WinDev(value=self.__code,id=dict(type='window-text-editor',index=self.name)) if dev
                else WinError(self.error) if self.error
                else self.__layout,
            default=window_default,
            position=self.position,
            size=self.size,
            id=dict(type='window-rnd',index=self.name),
            dragHandleClassName='windowHeader',
            dragGrid=dragGrid,
            resizeGrid=resizeGrid,
            # resizeHandleClasses={'topLeft':'resizeHandler','topRight':'resizeHandler','bottomLeft':'resizeHandler','bottomRight':'resizeHandler'},
        )

    def __build(self):
        self.__layout = ''
        self.error = ''
        if self.code:
            try:
                layout = ''
                _locals = locals()
                # layout may change inside self.code
                exec(self.code,globals(),_locals)
                print('locals',_locals)
                layout = _locals['layout']
                self.__layout = layout
            except Exception as e:
                self.error = e
                print('Error: ',e)
    
    @property
    def layout(self):
        return self.__layout

    @property
    def name(self):
        return self.__name
    
    @property
    def code(self):
        return self.__code
    
    @code.setter
    def code(self,new_code:str):
        self.__code = new_code
        self.__build()
    
    @classmethod
    def add(cls,name:str=''):
        name = '' if name in cls.__windows.keys() else name
        w = Window(name)
        cls.__windows[w.name] = w

    @classmethod
    def get(cls,name:str=''):
        if name == '':
            return cls.__windows
        for win in cls.__windows.values():
            if win.name == name:
                return win
        return None

    @classmethod
    def rm(cls,name:str):
        for n in cls.__windows.keys():
            if n == name:
                w = cls.__windows[n]
                del cls.__windows[n]
                return w
        return None

    @classmethod
    @property
    def names(cls):
        return list(cls.__windows.keys())



@callback(
    Output({'type':'window-text-editor','index':MATCH},'value'),
    Input({'type':'window-text-editor','index':MATCH},'value'),
    prevent_initial_call=True,
)
def window_text_editor_value(value):
    win = Window.get(ctx.triggered_id['index'])
    if win:
        win.code = value
    return value

@callback(
    Output({'type':'window-rnd','index':MATCH},'position'),
    Input({'type':'window-rnd','index':MATCH},'position'),
    prevent_initial_call=True,
)
def window_text_ernd_position(position):
    win = Window.get(ctx.triggered_id['index'])
    if win:
        win.position = position
    return position

@callback(
    Output({'type':'window-rnd','index':MATCH},'size'),
    Input({'type':'window-rnd','index':MATCH},'size'),
    prevent_initial_call=True,
)
def window_text_ernd_size(size):
    win = Window.get(ctx.triggered_id['index'])
    if win:
        win.size = size
    return size


if __name__ == '__main__':
    from dash import html
    Window.add('w1')
    w1 = Window.get('w1')
    w1.code='layout=html.Div("Hello World")'
    print(w1.layout)