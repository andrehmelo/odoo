# Bulk Delete Operations

## Overview
The delete wizard has been completely redesigned to provide more granular control over vehicle and maintenance record deletion.

## New Options

### 1. Delete Everything
- **Action**: Removes all vehicles and all maintenance records
- **Impact**: Complete database wipe of vehicles and interventions
- **Result**: Empty vehicle list and empty intervention history

### 2. Delete All Vehicles  
- **Action**: Removes all vehicles, preserves completed maintenance history
- **Impact**: All vehicles deleted, active interventions removed first
- **Result**: No vehicles remain, but completed maintenance records are preserved for historical reference

### 3. Remove Current Interventions
- **Action**: Removes only active interventions
- **Impact**: Vehicles in maintenance return to "Available" status
- **Result**: No vehicles deleted, all active interventions removed, vehicles become available
- **Note**: Same logic as the "Remove from Maintenance" action in vehicle forms/kanban

### 4. Remove Completed Maintenances
- **Action**: Deletes all completed maintenance records from history
- **Impact**: Only completed maintenance records are removed
- **Result**: Vehicles and active interventions remain untouched, history cleaned

### 5. Remove All Maintenances
- **Action**: Removes all maintenance records (current and completed)
- **Impact**: Vehicles in maintenance return to "Available" status
- **Result**: No vehicles deleted, all intervention history cleared, vehicles become available

## Key Features

### Smart Vehicle Status Management
- When removing current interventions, vehicles automatically return to "Available" status
- No vehicles are deleted when removing interventions
- Vehicle status is preserved correctly based on the operation

### Preview Before Action
- Shows count of items that will be affected
- Dynamic counter updates based on selected option
- Clear explanation of each option's impact

### Safety Confirmations
- Checkbox confirmation required
- Warning alerts displayed
- Cannot be undone warning
- Detailed explanation of each option

### Auto-refresh
- After any operation, the vehicle list automatically refreshes
- Success notification shows the results
- Clean user experience

## Menu Location
**Vehicles > Bulk Delete Operations**

## Usage Examples

### Example 1: Clean Up Test Data
Use "Delete Everything" to completely reset your vehicle database during testing.

### Example 2: End of Year Cleanup
Use "Remove Completed Maintenances" to archive old maintenance records and keep the database lean.

### Example 3: Cancel All Active Interventions
Use "Remove Current Interventions" to bring all vehicles back from maintenance without deleting any records.

### Example 4: Data Migration
Use "Delete All Vehicles" when you want to reimport vehicles but keep historical maintenance data for reporting.

## Technical Implementation

### Logic Flow for Current Interventions
```python
1. Find all interventions with state='in_maintenance'
2. For each intervention:
   - Set vehicle.status = 'available'
   - Delete the intervention record
3. Return success notification
4. Auto-refresh vehicle list
```

### Cascade Behavior
- Deleting a vehicle cascades to its interventions (due to ondelete='cascade')
- Deleting interventions does NOT delete vehicles
- Completed maintenances can exist without vehicles (orphaned records)

## Safety Measures
- Confirmation checkbox required
- UserError raised if no records found
- Clear preview of impact
- Success messages show exact count of affected records
