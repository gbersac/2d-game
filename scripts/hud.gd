extends CanvasLayer

@onready var money_label: Label = $MoneyLabel


func _ready() -> void:
	_update_label(GameState.money)
	GameState.money_changed.connect(_update_label)


func _update_label(amount: int) -> void:
	money_label.text = str(amount)
