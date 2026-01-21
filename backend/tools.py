import re
import random
from typing import Dict, List, Any
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field


class DiceRollInput(BaseModel):
    """Input schema for dice roll tool"""
    dice_notation: str = Field(
        description="Dice notation in format like '3d6', '1d20', '2d10+5', or '1d4-2'"
    )


class DiceRollerTool(BaseTool):
    """Tool for rolling dice in various formats (e.g., 3d6, 1d20, 2d10+5)"""
    
    name = "dice_roller"
    description = """Roll dice in standard notation format. 
    Examples: 
    - '3d6' rolls three 6-sided dice
    - '1d20' rolls one 20-sided die
    - '2d10+5' rolls two 10-sided dice and adds 5
    - '1d4-2' rolls one 4-sided die and subtracts 2
    
    Format: XdY[+/-Z] where:
    - X is the number of dice (optional, defaults to 1)
    - Y is the number of sides on each die
    - Z is an optional modifier to add or subtract"""
    
    args_schema = DiceRollInput
    
    def _run(self, dice_notation: str) -> str:
        """Execute the dice roll"""
        result = roll_dice(dice_notation)
        
        if result.get("error"):
            return f"Error: {result['error']}"
        
        # Format the response
        rolls_str = ", ".join(map(str, result["rolls"]))
        total = result["total"]
        modifier = result.get("modifier", 0)
        
        if modifier != 0:
            modifier_str = f" {'+' if modifier > 0 else ''}{modifier}"
            return f"Rolled {dice_notation}: [{rolls_str}]{modifier_str} = {total}"
        else:
            return f"Rolled {dice_notation}: [{rolls_str}] = {total}"
    
    async def _arun(self, dice_notation: str) -> str:
        """Async execution (not implemented)"""
        raise NotImplementedError("Async execution not supported")


def roll_dice(dice_notation: str) -> Dict[str, Any]:
    """
    Roll dice based on standard dice notation.
    
    Supports formats:
    - "3d6" - roll 3 six-sided dice
    - "1d20" - roll 1 twenty-sided die
    - "2d10+5" - roll 2 ten-sided dice and add 5
    - "1d4-2" - roll 1 four-sided die and subtract 2
    - "d6" - roll 1 six-sided die (number defaults to 1)
    
    Args:
        dice_notation: String in format XdY[+/-Z]
        
    Returns:
        Dictionary with:
        - "rolls": List of individual die rolls
        - "total": Sum of rolls plus modifier
        - "modifier": The modifier value (0 if none)
        - "error": Error message if parsing failed (None if successful)
    """
    # Normalize the input (remove whitespace, convert to lowercase)
    dice_notation = dice_notation.strip().lower()
    
    # Pattern to match dice notation: optional number, 'd', number, optional +/- modifier
    # Examples: "3d6", "d20", "2d10+5", "1d4-2"
    pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
    
    match = re.match(pattern, dice_notation)
    
    if not match:
        return {
            "error": f"Invalid dice notation: '{dice_notation}'. Expected format: XdY[+/-Z] (e.g., '3d6', '1d20', '2d10+5')",
            "rolls": [],
            "total": 0,
            "modifier": 0
        }
    
    # Extract components
    num_dice_str = match.group(1)
    num_sides_str = match.group(2)
    modifier_str = match.group(3)
    
    # Parse number of dice (defaults to 1 if not specified)
    try:
        num_dice = int(num_dice_str) if num_dice_str else 1
    except ValueError:
        return {
            "error": f"Invalid number of dice: '{num_dice_str}'",
            "rolls": [],
            "total": 0,
            "modifier": 0
        }
    
    # Parse number of sides
    try:
        num_sides = int(num_sides_str)
    except ValueError:
        return {
            "error": f"Invalid number of sides: '{num_sides_str}'",
            "rolls": [],
            "total": 0,
            "modifier": 0
        }
    
    # Parse modifier (defaults to 0 if not specified)
    modifier = 0
    if modifier_str:
        try:
            modifier = int(modifier_str)
        except ValueError:
            return {
                "error": f"Invalid modifier: '{modifier_str}'",
                "rolls": [],
                "total": 0,
                "modifier": 0
            }
    
    # Validate inputs
    if num_dice < 1:
        return {
            "error": f"Number of dice must be at least 1, got {num_dice}",
            "rolls": [],
            "total": 0,
            "modifier": 0
        }
    
    if num_dice > 100:
        return {
            "error": f"Number of dice cannot exceed 100, got {num_dice}",
            "rolls": [],
            "total": 0,
            "modifier": 0
        }
    
    if num_sides < 2:
        return {
            "error": f"Number of sides must be at least 2, got {num_sides}",
            "rolls": [],
            "total": 0,
            "modifier": 0
        }
    
    if num_sides > 1000:
        return {
            "error": f"Number of sides cannot exceed 1000, got {num_sides}",
            "rolls": [],
            "total": 0,
            "modifier": 0
        }
    
    # Roll the dice
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    
    # Calculate total
    total = sum(rolls) + modifier
    
    return {
        "rolls": rolls,
        "total": total,
        "modifier": modifier,
        "error": None
    }


# Create an instance of the tool for easy import
dice_roller_tool = DiceRollerTool()
