extends Node2D

@onready var hint: Label = $CanvasLayer/Hint


func _unhandled_input(event: InputEvent) -> void:
	if (
		event.is_action_pressed("move_left")
		or event.is_action_pressed("move_right")
		or event.is_action_pressed("move_up")
		or event.is_action_pressed("move_down")
	):
		hint.visible = false
