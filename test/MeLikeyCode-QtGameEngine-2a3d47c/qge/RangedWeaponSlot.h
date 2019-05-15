#ifndef RANGEDWEAPONSLOT_H
#define RANGEDWEAPONSLOT_H

#include "Vendor.h"

#include "Slot.h"

namespace qge{

class EquipableItem;

class RangedWeaponSlot : public Slot
{
public:
    bool canBeEquipped(EquipableItem *item);
    void use();
};

}
#endif
