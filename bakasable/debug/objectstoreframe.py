import tkinter as tk

import pygame
import PIL.Image
import PIL.ImageTk

from bakasable.debug.storeframe import StoreFrame


class ObjectStoreFrame(StoreFrame):

    def create_widgets(self):
        super().create_widgets()

        self.filter_coordinated = tk.IntVar()
        self.coordinated_checkbox = tk.Checkbutton(
            self.list_frame,
            text='Coordinated',
            variable=self.filter_coordinated)
        self.coordinated_checkbox.pack(side='top', anchor='nw')

        self.object_info = tk.Text(
            self, wrap='word', state=tk.DISABLED)

        self.sprite_frame = tk.Frame(self, width=200)
        self.sprite = tk.Label(self.sprite_frame)
        self.sprite.pack(expand=True)
        self.sprite_frame.pack_propagate(0)
        self.sprite_frame.pack(side='right', fill='y')

        self.object_info.tag_configure('title', font=('Times', '14', 'bold'))
        self.object_info.pack(side='right', fill='both', expand=True)

        self.selected_entity = None
        self.after(500, self.update_info_view)

    def id_to_value(self, uid):
        obj = self.context.object_store.get(uid, expend_chunk=False)
        return '%s#%d' % (type(obj).__name__, obj.uid)

    def value_to_id(self, value):
        return int(value.split('#')[1])

    def on_list_selected_change(self, evt):
        selected = self.list.curselection()
        if selected:
            value = self.list.get(selected[0])
            uid = int(value.split('#')[1])
            self.selected_entity = self.context.object_store.get(
                uid, expend_chunk=False)
            self.update_info_view(False)

    def update_info_view(self, call=True):
        if call:
            self.after(500, self.update_info_view)
        if not self.selected_entity:
            return
        self.object_info['state'] = tk.NORMAL
        self.object_info.delete('1.0', tk.END)
        self.object_info.insert(
            tk.END, '%s#%d\n' % (
                type(self.selected_entity).__name__, self.selected_entity.uid),
            'title')
        for key in self.selected_entity.attr:
            self.object_info.insert(
                tk.END, '    \u25CF %s=%s\n' % (
                    key, getattr(self.selected_entity, key)))

        coordinator = self.context.peer_store \
            .get_closest_uid(self.selected_entity.uid)
        self.object_info.insert(tk.END, 'coordinator: %d' % coordinator)
        self.object_info['state'] = tk.DISABLED
        if self.selected_entity.current_frame:
            img_str = pygame.image.tostring(
                self.selected_entity.current_frame, 'RGBA')
            rect = self.selected_entity.current_frame.get_rect()
            img = PIL.Image.frombytes('RGBA', (rect.w, rect.h), img_str)
            img.thumbnail((200, 200))

            self.tk_img = PIL.ImageTk.PhotoImage(img)
            self.sprite['image'] = self.tk_img
            self.sprite.pack()
        else:
            self.sprite['image'] = ''
