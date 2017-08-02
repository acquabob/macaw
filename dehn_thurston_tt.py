r"""

Dehn Thurston train tracks

AUTHORS:

- BALAZS STRENNER (2017-07-30): initial version


"""

#*****************************************************************************
#       Copyright (C) 2017 Balazs Strenner <strennerb@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************


from surface import Surface 
from train_track import TrainTrack
from pants_decomposition import PantsDecomposition
from sage.structure.sage_object import SageObject
from sage.all import sign

LEFT = 0
RIGHT = 1

UP = 0
TWO_SIDED = 1




class BranchMap(SageObject):
    def __init__(self,branches):
        """
        EXAMPLES:

        sage: from sage.topology.dehn_thurston_tt import BranchMap
        sage: bm = BranchMap([2,-4,5,-6,1])
        sage: bm._branch_map[4]
        [4]
        sage: bm._branch_map[2]
        [2]
        """
        self._branch_map = {abs(b):[abs(b)] for b in branches}

    def branch_list(self,branch):
        """
        EXAMPLES:

        sage: from sage.topology.dehn_thurston_tt import BranchMap
        sage: bm = BranchMap([2,-4,5,-6,1])
        sage: bm.branch_list(4)
        [4]
        sage: bm.branch_list(-4)
        [-4]
        sage: bm.branch_list(2)
        [2]
        sage: bm.branch_list(-2)
        [-2]
        """
        if branch > 0:
            return self._branch_map[branch]
        else:
            return list(reversed([-b for b in self._branch_map[-branch]]))

    def append(self,append_to, appended_branch):
        """
        EXAMPLES:

        sage: from sage.topology.dehn_thurston_tt import BranchMap
        sage: bm = BranchMap([2,-4,5,-6,1])
        sage: bm.append(2, -4)
        sage: bm.branch_list(2)
        [2, -4]
        sage: bm.append(-2, 5)
        sage: bm.branch_list(2)
        [-5, 2, -4]
        sage: bm.branch_list(-2)
        [4, -2, 5]
        sage: bm.append(-1, -2)
        sage: bm.branch_list(1)
        [-5, 2, -4, 1]
        sage: bm.branch_list(-1)
        [-1, 4, -2, 5]
        """
        if append_to > 0:
            self._branch_map[append_to].extend(self.branch_list(appended_branch))
        else:
            self._branch_map[-append_to][0:0] = self.branch_list(-appended_branch)




class DehnThurstonTT(TrainTrack):
    # def __init__(self):
    #     pass

    def get_turning(self, switch):
        """
        
        TESTS: 

            sage: from sage.topology.dehn_thurston_tt import DehnThurstonTT
            sage: tt = DehnThurstonTT([[8, 6, 5], [-8, 2, -6], [-5, -2, 4], [-1, -3, -4], [3, 9, 7], [-9, 1, -7]])
            sage: tt.get_turning(1)
            0
            sage: tt.get_turning(-1)
            0
            sage: tt.get_turning(2)
            1
            sage: tt.get_turning(-2)
            1
            sage: tt.get_turning(3)
            1
            sage: tt.get_turning(-2)
            1

        """
        for side in [LEFT,RIGHT]:
            if self.outgoing_branch(switch, 0, side) == \
               -self.outgoing_branch(-switch, 0, side):
                return side
        assert(False)

    def elem_move_type(self, pants_curve):

        # it is first elementary move if and only if there are two outgoing
        # branches in opposite directions whose endpoint is the same switch
        # which is different from the starting switch

        for i in self.outgoing_branches(pants_curve):
            sw1 = self.branch_endpoint(i)
            if abs(sw1) == abs(pants_curve):
                continue
            for j in self.outgoing_branches(-pants_curve):
                sw2 = self.branch_endpoint(j)
                if sw1 == sw2:
                    return 1
        return 2

    def torus_boundary_switch(self, switch):
        """
        Return the switch on the boundary of the torus containing ``switch``.

        The returned switch is oriented so that the torus is on its left side.
        """
        assert(self.elem_move_type(switch) == 1)
        for b in self.outgoing_branches(switch):
            new_switch = self.branch_endpoint(b)
            if abs(new_switch) != abs(switch):
                break
        if self.get_turning(new_switch) == LEFT:
            return -new_switch
        return new_switch
            
    
    def orientation_of_switch_first_move(self, switch):
        """
        Return the standard orientation of the switch for the first elementary
        move.
        """
        assert(self.elem_move_type(switch) == 1)
        bdy_switch = self.torus_boundary_switch(switch)
        turning = self.get_turning(bdy_switch)
        if turning == RIGHT:
            b = self.outgoing_branch(bdy_switch, 0)
        else:
            b = self.outgoing_branch(-bdy_switch, 1)
        sw = self.branch_endpoint(b)
        if self.get_turning(switch) == LEFT:
            return sw
        return -sw
        
    
    def num_curves_on_sides(self, pants_curve):
        switch = pants_curve
        top_branches = self.outgoing_branches(switch)
        bottom_branches = self.outgoing_branches(-switch)
        ntop = len(top_branches)
        nbottom = len(bottom_branches)

        turning = self.get_turning(pants_curve)
        return (nbottom-1,ntop-1) if turning == LEFT else (ntop-1,nbottom-1)


    def unzip_with_collapse(self, switch, pos, collapse_type, branch_map=None,
                            start_side=LEFT, debug=False):
        r"""
        The train track for the first elementary move, when `t_1>0` and
        `\lambda_{23}` is present.
        Performing the unzipping according to `r<t_1`.

            sage: LEFT = 0
            sage: RIGHT = 1
            sage: UP = 0
            sage: TWO_SIDED = 1
            sage: from sage.topology.dehn_thurston_tt import DehnThurstonTT
            sage: tt = DehnThurstonTT([[-1,2,3], [-2,4,-3], [5], [-5,-4,1]], [11, 3, 100, 11, 2])
            sage: tt.unzip_with_collapse(1,0,UP,start_side = LEFT)
            0
            sage: tt._measure
            [11, 3, 89, 11, 2]
        
        Now performing the unzipping according to `r>t_1`.

            sage: tt = DehnThurstonTT([[-1,2,3], [-2,4,-3], [5], [-5,-4,1]], [100, 3, 11, 100, 2])
            sage: tt.unzip_with_collapse(1,0,UP,start_side=LEFT)
            1
            sage: tt._measure
            [89, 3, 11, 11, 2]

        The train track for the first elementary move, when ``t_1<0`` and
        ``\lambda_{23}`` is present.
        Performing the unzipping according to `r<t_1`.

            sage: tt = DehnThurstonTT([[1,-2,3], [-1,-4,2], [5], [-5,-3,4]], [100, 5, 11, 11, 2])
            sage: tt.unzip_with_collapse(1,0,UP,start_side=RIGHT)
            0
            sage: tt._measure
            [89, 5, 11, 11, 2]
        
        Now performing the unzipping according to `r>t_1`.

            sage: tt = DehnThurstonTT([[1,-2,3], [-1,-4,2], [5], [-5,-3,4]], [11, 5, 100, 100, 2])
            sage: tt.unzip_with_collapse(1,0,UP,start_side=RIGHT)
            1
            sage: tt._measure
            [11, 5, 89, 11, 2]

        The next train track is a has a left-twisting annulus. We perform an
        unzip not next to the core curve of the annulus but in the next cusp
        that goes into the core curve.

            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]], [100, 1, 5, 6, 6, 5, 1])
            sage: tt.unzip_with_collapse(1,1,TWO_SIDED,start_side=RIGHT)
            0
            sage: tt._measure
            [89, 1, 5, 6, 6, 5, 1]
      
        Now we unzip at the same cusp, going into the third branch on the other
        side:: 

            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]], [10, 6, 15, 3, 3, 15, 6])
            sage: tt.unzip_with_collapse(1,1,TWO_SIDED,start_side=RIGHT)
            2
            sage: tt._measure
            [5, 6, 15, 3, 3, 10, 6]

        The next train track is a has a right-twisting annulus. We perform an
        unzip not next to the core curve of the annulus but in the next cusp
        that goes into the core curve.

            sage: tt = DehnThurstonTT([[2, 3, 4, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]], [100, 1, 5, 6, 6, 5, 1])
            sage: tt.unzip_with_collapse(1,1,TWO_SIDED,start_side=LEFT)
            0
            sage: tt._measure
            [94, 1, 5, 6, 6, 5, 1]

        Now we unzip at the same cusp, going into the third branch on the other
        side:: 

            sage: tt = DehnThurstonTT([[2, 3, 4, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]], [10, 8, 15, 6, 6, 15, 8])
            sage: tt.unzip_with_collapse(1,1,TWO_SIDED,start_side=LEFT)
            2
            sage: tt._measure
            [5, 8, 15, 6, 6, 10, 8]


        """
        debug = False
        if debug:
            print "---------------------------"
            print "BEGIN: unzip_with_collapse()"
            print "---------------------------"
            print "switch:", switch
            print "pos:", pos
            print "start_side:", "LEFT" if start_side == LEFT else "RIGHT"

        unzip_pos, meas1, meas2 = self.unzip_pos(switch, pos, start_side)

        if debug:
            print "Unzipped measures:", meas1, meas2
            print "Unzip pos:",  unzip_pos
        unzip_br = self.outgoing_branch(-switch, unzip_pos,
                                        (start_side+1)%2)
        if collapse_type == UP:
            collapsed_branch = self.outgoing_branch(switch, 0, start_side)
        elif collapse_type == TWO_SIDED:
            pants_branch = self.outgoing_branch(switch, 0, (start_side+1)%2)
            
        if debug:
            print "Unzip branch:", unzip_br

        # performing the unzip
        self.unzip_with_collapse_no_measure(switch, pos, unzip_pos,
                                            collapse_type, branch_map,
                                            start_side, debug)


        if not self.is_measured():
            return
        
        # updating the measure        
        if collapse_type == UP:
            if debug:
                print "Collapsed branch: ", collapsed_branch
            self._set_measure(unzip_br, meas2)
            self._set_measure(collapsed_branch, meas1)
        elif collapse_type == TWO_SIDED:
            if unzip_pos == 0:
                self._set_measure(pants_branch, meas2)
            else:
                self._set_measure(unzip_br, meas2)
                self._set_measure(pants_branch, meas1)

        return unzip_pos


    # def _update_branch_map_UP(self,switch,pos,unzip_pos,branch_map,
    #                           start_side=LEFT):
    #     if start_side == LEFT:
    #     branches_to_update = self.outgoing_branches(-switch)[

    
    # @staticmethod
    # def _append_branch_map(branch_map,branch,appended_branch):
    #     if branch > 0:
    #     pass
    
    def unzip_with_collapse_no_measure(self, switch, pos, unzip_pos,
                                       collapse_type, branch_map=None,
                                       start_side=LEFT, debug=False):

        r"""

        EXAMPLES:

        The train track for the first elementary move, when `t_1>0` and
        `\lambda_{23}` is present.
        Performing the unzipping according to `r<t_1`.

            sage: LEFT = 0
            sage: RIGHT = 1
            sage: UP = 0
            sage: TWO_SIDED = 1
            sage: from sage.topology.dehn_thurston_tt import DehnThurstonTT
            sage: tt = DehnThurstonTT([[-1,2,3], [-2,4,-3], [5], [-5,-4,1] ])
            sage: tt.unzip_with_collapse_no_measure(1,0,0,UP,start_side = LEFT)
            sage: tt._gluing_list
            [[2, -1, 3], [-2, 4, -3], [5], [-5, -4, 1]]
            sage: tt._branch_endpoint
            [[-2, 1, 1, -1, 2], [1, -1, -1, -2, -2]]

        Now performing the unzipping according to `r>t_1`.

            sage: tt = DehnThurstonTT([[-1,2,3], [-2,4,-3], [5], [-5,-4,1] ])
            sage: tt.unzip_with_collapse_no_measure(1,0,1,UP,start_side=LEFT)
            sage: tt._gluing_list
            [[2, 3], [-2, 4], [5], [-5, -1, -4, 1, -3]]
            sage: tt._branch_endpoint
            [[-2, 1, 1, -1, 2], [-2, -1, -2, -2, -2]]
        
        The train track for the first elementary move, when ``t_1<0`` and
        ``\lambda_{23}`` is present.
        Performing the unzipping according to `r<t_1`.

            sage: tt = DehnThurstonTT([[1,-2,3], [-1,-4,2], [5], [-5,-3,4] ])
            sage: tt.unzip_with_collapse_no_measure(1,0,0,UP,start_side=RIGHT)
            sage: tt._gluing_list
            [[1, 3, -2], [-1, -4, 2], [5], [-5, -3, 4]]
            sage: tt._branch_endpoint
            [[1, -1, 1, -2, 2], [-1, 1, -2, -1, -2]]

        Now performing the unzipping according to `r>t_1`.

            sage: tt = DehnThurstonTT([[1,-2,3], [-1,-4,2], [5], [-5,-3,4] ])
            sage: tt.unzip_with_collapse_no_measure(1,0,1,UP,start_side=RIGHT)
            sage: tt._gluing_list
            [[1, -2], [-4, 2], [5], [-5, -1, -3, 4, 3]]
            sage: tt._branch_endpoint
            [[1, -1, -2, -2, 2], [-2, 1, -2, -1, -2]]

        The next train track is a has a left-twisting annulus. We perform an
        unzip not next to the core curve of the annulus but in the next cusp
        that goes into the core curve.

            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]])
            sage: tt.unzip_with_collapse_no_measure(1,1,0,TWO_SIDED,start_side=RIGHT)

            sage: tt._gluing_list
            [[1, 3, 4, 2], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._branch_endpoint
            [[1, 1, 1, 1, 2, 3, 4], [-1, -2, -3, -4, -1, -1, -1]]
      
        Now we unzip at the same cusp, going into the third branch on the other
        side:: 

            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]])
            sage: tt.unzip_with_collapse_no_measure(1,1,2,TWO_SIDED,start_side=RIGHT)
            sage: tt._gluing_list
            [[3, 4, 2], [-6, -7, -5, 1], [5], [-2], [6, -1], [-3], [7], [-4]]
            sage: tt._branch_endpoint
            [[-1, 1, 1, 1, 2, 3, 4], [3, -2, -3, -4, -1, -1, -1]]

        The next train track is a has a right-twisting annulus. We perform an
        unzip not next to the core curve of the annulus but in the next cusp
        that goes into the core curve.

            sage: tt = DehnThurstonTT([[2, 3, 4, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]])
            sage: tt.unzip_with_collapse_no_measure(1,1,0,TWO_SIDED,start_side=LEFT)

            sage: tt._gluing_list
            [[4, 2, 3, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._branch_endpoint
            [[1, 1, 1, 1, 2, 3, 4], [-1, -2, -3, -4, -1, -1, -1]]
      
        Now we unzip at the same cusp, going into the third branch on the other
        side:: 

            sage: tt = DehnThurstonTT([[2, 3, 4, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]])
            sage: tt.unzip_with_collapse_no_measure(1,1,2,TWO_SIDED,start_side=LEFT)
            sage: tt._gluing_list
            [[4, 2, 3], [1, -7, -5, -6], [5], [-2], [-1, 6], [-3], [7], [-4]]
            sage: tt._branch_endpoint
            [[-1, 1, 1, 1, 2, 3, 4], [3, -2, -3, -4, -1, -1, -1]]


        """



        if collapse_type == UP:
            assert(pos==0)
        elif collapse_type == TWO_SIDED:
            pants_branch_pos = 0 if start_side == RIGHT else -1
            assert(self.outgoing_branches(switch)[pants_branch_pos] ==
                   -self.outgoing_branches(-switch)[pants_branch_pos])


            
        unzip_branch = self.outgoing_branch(-switch, unzip_pos, (start_side+1)%2)
        bottom_switch = self.branch_endpoint(unzip_branch)
        # if -switch == bottom_switch and unzip_pos > end_index:
        #     unzip_pos += 1

        debug = False
        if debug:
            print "---------------------------"
            print "BEGIN: unzip_with_collapse_no_measure()"
            print "---------------------------"
            print "Unzip branch: ", unzip_branch
            print "Bottom switch: ", bottom_switch
            print "Corrected unzip_pos:", unzip_pos

        # dealing with collapsed branches
        if collapse_type == UP:
            # cut the collapsed branch off the starting switch and gluing it to
            # the bottom switch
            if start_side == LEFT:
                collapsed_branch = self.outgoing_branches(switch).pop(0)
            else:
                collapsed_branch = self.outgoing_branches(switch).pop(-1)                
        # we do this after the pop in case bottom_switch == switch
        end_index = self.outgoing_branches(bottom_switch).index(-unzip_branch)

        if collapse_type == UP:        
            if debug:
                print "End index:", end_index
                print "Collapsed branch:", collapsed_branch
            assert(collapsed_branch != -unzip_branch)

            insert_pos = end_index if start_side == LEFT else \
                         end_index + 1
            if debug:
                print "Insert pos:", insert_pos
            self.outgoing_branches(bottom_switch).insert(insert_pos,
                                                       collapsed_branch)


            # move branches            
            bottom_branches = self.outgoing_branches(-switch)
            n = len(bottom_branches)
            if start_side == LEFT:
                branches_to_move = bottom_branches[n-unzip_pos:]
                del bottom_branches[n-unzip_pos:]
            else:
                branches_to_move = bottom_branches[:unzip_pos]
                del bottom_branches[:unzip_pos]
            top_switch = self.branch_endpoint(collapsed_branch)
            k = self.outgoing_branches(top_switch).index(-collapsed_branch)
            if start_side == LEFT:
                insert_pos = k+1
            else:
                insert_pos = k
            self.outgoing_branches(top_switch)[insert_pos:insert_pos] = \
                                                        branches_to_move
            self._set_endpoint(-collapsed_branch,bottom_switch)
            for branch in branches_to_move:
                self._set_endpoint(-branch,top_switch)


            if branch_map != None:
                # update branch map for the other branches
                for branch in branches_to_move:
                    branch_map.append(-branch,collapsed_branch)

                # update branch map of collapsed_branch
                branch_map.append(-collapsed_branch,unzip_branch)
            


        elif collapse_type == TWO_SIDED:

            # moving the top branches
            top = self.outgoing_branches(switch)
            n = len(top)
            if start_side == LEFT:
                branches_to_move = self.outgoing_branches(switch)[:pos+1]
                top[-1:-1] = branches_to_move
                del top[:-n]
            else:
                branches_to_move = self.outgoing_branches(switch)[-pos-1:]
                top[1:1] = branches_to_move
                del top[n:]

            if unzip_pos > 0:

                pop_pos = -1 if start_side == LEFT else 0
                collapsed_branch = self.outgoing_branches(switch).pop(pop_pos)
                self.outgoing_branches(-switch).pop(pop_pos)
                # pos -= 1

                # top.insert(0,top[pos:])
                # del top[n:]
                bottom = self.outgoing_branches(-switch)
                m = len(bottom)
                # the pants branch has already been removed
                if start_side == LEFT:
                    bottom[0:0] = bottom[m+1-unzip_pos:]
                    del bottom[m:]
                    bottom.insert(0, collapsed_branch)
                else:
                    bottom.extend(bottom[:unzip_pos-1])
                    del bottom[:-m]
                    bottom.append(collapsed_branch)

                k = self.outgoing_branches(bottom_switch).index(-unzip_branch)
                insert_pos = k if start_side == LEFT else k+1
                self.outgoing_branches(bottom_switch).insert(insert_pos,
                                                             -collapsed_branch)

                self._set_endpoint(-collapsed_branch,-switch)
                self._set_endpoint(collapsed_branch,bottom_switch)


    def unzip_fold_general_twist(self, pants_curve, twists_on_left,
                                 twists_on_right):
        """
        EXAMPLES:

        We only twist in the good direction::

            sage: from sage.topology.dehn_thurston_tt import DehnThurstonTT
            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]], [1, 2, 3, 4, 5, 6, 7])
            sage: tt.unzip_fold_general_twist(1, -2, -1)
            sage: tt._gluing_list
            [[1, 3, 4, 2], [-1, -7, -5, -6], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._branch_endpoint
            [[1, 1, 1, 1, 2, 3, 4], [-1, -2, -3, -4, -1, -1, -1]]
            sage: tt._measure
            [14, 2, 3, 4, 5, 6, 7]

        There is twist in the good direction on the left side and in the wrong
        direction on the right side. The unzip on the right goes into the pants branch.

            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]], [10, 2, 3, 4, 5, 6, 7])
            sage: tt.unzip_fold_general_twist(1, -2, 1)
            sage: tt._gluing_list
            [[1, 4, 2, 3], [-1, -7, -5, -6], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._branch_endpoint
            [[1, 1, 1, 1, 2, 3, 4], [-1, -2, -3, -4, -1, -1, -1]]
            sage: tt._measure
            [17, 2, 3, 4, 5, 6, 7]

        There is bad twist on both sides, but both unzips go into the pants
        curve.

            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]], [100, 2, 3, 13, 5, 6, 7])
            sage: tt.unzip_fold_general_twist(1, 2, 1)
            sage: tt._gluing_list
            [[1, 4, 2, 3], [-1, -6, -7, -5], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._branch_endpoint
            [[1, 1, 1, 1, 2, 3, 4], [-1, -2, -3, -4, -1, -1, -1]]
            sage: tt._measure
            [74, 2, 3, 13, 5, 6, 7]
        
        (We peel of a 6, 7 and 13 from the pants branch.)
        
        Now we we consider a right-turning train track, with bad twist on the
        right, where the unzip goes across.

            sage: tt = DehnThurstonTT([[2, 3, 4, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]], [1, 2, 3, 13, 5, 6, 7])
            sage: tt.unzip_fold_general_twist(1, 0, -1)
            sage: tt._gluing_list
            [[1, -6, -7, -5], [-1, 2, 3, 4], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._branch_endpoint
            [[1, -1, -1, -1, 2, 3, 4], [-1, -2, -3, -4, 1, 1, 1]]
            sage: tt._measure
            [4, 2, 3, 13, 5, 6, 7]

        The next one is a right-turning train track which has a bad twist on
        both sides. The unzips also go across.

            sage: tt = DehnThurstonTT([[2, 3, 4, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]], [1, 2, 3, 13, 5, 6, 7])
            sage: tt.unzip_fold_general_twist(1, -1, -1)
            sage: tt._gluing_list
            [[1, -6, -7, -5], [-1, 3, 4, 2], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._measure
            [6, 2, 3, 13, 5, 6, 7]


        """
        debug = False

        switch = pants_curve
        turning = self.get_turning(pants_curve)
        nleft, nright = self.num_curves_on_sides(pants_curve)
        # by rotating the pants curve, we can assume that the twists on the left
        # are between 0 and nleft-1 if right-turning and between -(nleft-1) and 0
        # if left-turning.
        if turning == RIGHT:
            # we fix the twists so that there is 0 to nright-1 twists on the right

            num_rotations = -(twists_on_right // nright)
            # if positive, we rotate "up", towards the positive direction of the
            # switch, otherwise we rotate down

            good_twists_on_fixed_side = twists_on_right % nright
            good_twists_on_other_side = twists_on_left - num_rotations * nleft
            nfixed_side = nright
            nother_side = nleft
        else:
            # we fix the twists so that there is (-nleft-1) to 0 twists on the left
            num_rotations = -((-twists_on_left) // nleft)

            good_twists_on_fixed_side = (-twists_on_left) % nleft
            # this is nonnegative, between 0 and nleft-1. This is how many branches we
            # will fold on the left.

            good_twists_on_other_side = -(twists_on_right + num_rotations * nright)
            # this is positive if the twists on the right are good twists (only
            # folding is needed, and negative if the twists are bad (unzipping is
            # needed)
            nfixed_side = nleft
            nother_side = nright

        if debug:
            print "----------------------------------------"
            print "BEGIN: unzip_fold_general_twist()"
            print "----------------------------------------"            
            print "Turning: ", 'LEFT' if turning == LEFT else 'RIGHT'
            print "Switch: ", switch
            print "Branches on left: ", nleft
            print "Branches on right: ", nright
            print "Branches on fixed side: ", nfixed_side
            print "Branches on other side: ", nother_side
            print "Number of rotations: ", num_rotations
            print "Twists on left (original): ", twists_on_left
            print "Twists on right (original): ", twists_on_right
            print "Good twists on fixed side: ", good_twists_on_fixed_side
            print "Good twists on other side: ", good_twists_on_other_side
            
        # doing folds on the fixed side
        for i in range(good_twists_on_fixed_side):
            # print "Fold fixed side"
            if debug:
                print i, self._gluing_list
                print i, self._measure

            self.fold(-switch,1,0,start_side = turning)

        if debug:
            print "After fixed side:", self._gluing_list
            print "After fixed side:", self._measure
            
        # doing folds on unzips on the other side. This involves the positive
        # direction of ``switch``.
        if good_twists_on_other_side > 0:
            # if there are only good twists, we fold
            for i in range(good_twists_on_other_side):
                self.fold(switch,1,0,start_side = turning)
        else:
            # otherwise we unzip

            while True:
                if debug:
                    print self._gluing_list
                    print self._measure
                # the positition of the first unzip
                pos = min(nother_side,-good_twists_on_other_side) - 1
                unzip_pos = self.unzip_with_collapse(switch,pos,TWO_SIDED,
                                                     start_side=(turning+1)%2)

                good_twists_on_other_side += pos + 1
                if debug:
                    print "pos:", pos
                    print "unzip_pos:", unzip_pos
                    print "Good twists left on other side:", \
                        good_twists_on_other_side
                if unzip_pos == 0:
                    # we unzipped into the pants curve
                    if good_twists_on_other_side == 0:
                        break
                else:
                    # we unzip into a branch on the other side

                    # find the endpoint of the unzipped branch
                    b = self.outgoing_branch(-switch,0,start_side=turning)
                    sw = self.branch_endpoint(b)
                    idx = self.outgoing_branch_index(sw,-b,start_side=turning)

                    if debug:
                        print "Unzipped branch:", b
                        print "Endpoint of unzipped branch:", sw
                        print "Index of unzipped branch at the endpoint", idx
                        print "Folding index ", idx, "onto index", idx+1, \
                            "from side", turning
                    # fold back one of the split branches on the other
                    # As a result, we get the pants curve back.
                    self.fold(sw,idx+1,idx,start_side=turning)
                    if debug:
                        print self._gluing_list
                        print self._measure
                    
                    # Fold up the branches there were pulled around the pants curve.
                    for i in range(unzip_pos-1):
                        self.fold(-switch,1,0,start_side=(turning+1)%2)
                        if debug:
                            print self._gluing_list
                            print self._measure

                    # Fold up all remaining branches on the other side
                    for i in range(-good_twists_on_other_side):
                        self.fold(switch,1,0,start_side=(turning+1)%2)
                        if debug:
                            print self._gluing_list
                            print self._measure
                        
                    # switch the orientation of the switch, because it was rotated
                    # by 180 degrees
                    self.change_switch_orientation(switch)
                    break


    def unzip_fold_pants_twist(self, pants_curve, power=1):
        r"""
        
        TESTS:

        Twisting in the good direction:

            sage: from sage.topology.dehn_thurston_tt import DehnThurstonTT
            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]], [1, 2, 3, 13, 5, 6, 7])
            sage: tt.unzip_fold_pants_twist(1, -1)
            sage: tt._gluing_list
            [[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._measure
            [19, 2, 3, 13, 5, 6, 7]

        Twisting in the bad direction, train track remains left-turning:

            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]], [100, 2, 3, 13, 5, 6, 7])
            sage: tt.unzip_fold_pants_twist(1, 1)
            sage: tt._gluing_list
            [[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._measure
            [82, 2, 3, 13, 5, 6, 7]

        Twisting in the bad direction, train track becomes right-turning:

            sage: tt = DehnThurstonTT([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]], [1, 2, 3, 13, 5, 6, 7])
            sage: tt.unzip_fold_pants_twist(1, 1)
            sage: tt._gluing_list
            [[-5, -6, -7, 1], [2, 3, 4, -1], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._measure
            [17, 2, 3, 13, 5, 6, 7]

        A right-turning example:

            sage: tt = DehnThurstonTT([[2, 3, 4, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]], [1, 2, 3, 13, 5, 6, 7])
            sage: tt.unzip_fold_pants_twist(1, -1)
            sage: tt._gluing_list
            [[1, -5, -6, -7], [-1, 2, 3, 4], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._measure
            [17, 2, 3, 13, 5, 6, 7]

        Direction of input switch does not matter:

            sage: tt = DehnThurstonTT([[2, 3, 4, 1], [-5, -6, -7, -1], [5], [-2], [6], [-3], [7], [-4]], [1, 2, 3, 13, 5, 6, 7])
            sage: tt.unzip_fold_pants_twist(-1, -1)
            sage: tt._gluing_list
            [[1, -5, -6, -7], [-1, 2, 3, 4], [5], [-2], [6], [-3], [7], [-4]]
            sage: tt._measure
            [17, 2, 3, 13, 5, 6, 7]


        """
        nright = self.num_curves_on_sides(pants_curve)[RIGHT]
        self.unzip_fold_general_twist(pants_curve, 0, power * nright)




    def unzip_fold_first_move_inverse(self, switch, branch_map=None):
        """
        TESTS:

            sage: from sage.topology.dehn_thurston_tt import DehnThurstonTT
            sage: tt = DehnThurstonTT([[1, 5], [-1, 4], [2, -8, 9, -7, -9], [-2, -5, 6, -4, -6], [7, 3], [8, -3]], [3, 20, 3, 10, 10, 13, 15, 15, 8])
            sage: tt.unzip_fold_first_move(1)
            sage: tt.unzip_fold_first_move_inverse(1)
            sage: tt._gluing_list
            [[1, 5], [-1, 4], [2, -8, 9, -7, -9], [-2, -5, 6, -4, -6], [7, 3], [8, -3]]
            sage: tt._branch_endpoint
            [[1, 2, 3, -1, 1, -2, 3, -3, 2], [-1, -2, -3, -2, -2, -2, 2, 2, 2]]
            sage: tt._measure
            [3, 20, 3, 10, 10, 13, 15, 15, 8]


            sage: tt = DehnThurstonTT([[1, 5], [-1, 4], [2, -8, 9, -7, -9], [-2, -5, 6, -4, -6], [7, 3], [8, -3]], [3, 20, 3, 10, 10, 13, 15, 15, 8])
            sage: tt.unzip_fold_first_move(1)
            sage: tt.unzip_fold_first_move_inverse(1)
            sage: tt._gluing_list
            [[1, 5], [-1, 4], [2, -8, 9, -7, -9], [-2, -5, 6, -4, -6], [7, 3], [8, -3]]
            sage: tt._branch_endpoint
            [[1, 2, 3, -1, 1, -2, 3, -3, 2], [-1, -2, -3, -2, -2, -2, 2, 2, 2]]
            sage: tt._measure
            [3, 20, 3, 10, 10, 13, 15, 15, 8]


        
        """
        for i in range(3):
            self.unzip_fold_first_move(switch)
        bdy_switch = self.torus_boundary_switch(switch)
        self.unzip_fold_pants_twist(bdy_switch,-1)

    def pants_branch_on_switch(self, switch):
        """
        TESTS: 

            sage: from sage.topology.dehn_thurston_tt import DehnThurstonTT
            sage: tt = DehnThurstonTT([[10, 6, 5], [-10, 4, -6], [-5, -4, 2], [-8, -7, -2], [7, 9, 13], [-9, 8, -13]])
            sage: tt.pants_branch_on_switch(1)
            10
            sage: tt.pants_branch_on_switch(-1)
            10
            sage: tt.pants_branch_on_switch(2)
            2
            sage: tt.pants_branch_on_switch(-2)
            2
            sage: tt.pants_branch_on_switch(3)
            13
            sage: tt.pants_branch_on_switch(-3)
            13

        """
        for side in [LEFT,RIGHT]:
            b1 = self.outgoing_branch(switch, 0, side)
            b2 = self.outgoing_branch(-switch, 0, side) 
            if b1 == -b2:
                return abs(b1)
        assert(False)


    def unzip_fold_first_move(self, switch, branch_map=None, inverse=False):
        r"""
        TESTS::

        The following is a Dehn-Thurston train track on the genus 2 surface.
        The pants decomposition has a separating curve (2), and switch 1 is
        left-turning, switches 2 and 3 are right-turning. Pants curves 1 and 3
        give first elementary moves.

        First we test the cases where unzipping goes into the pants curve.
        Testing the inverse elementary moves as well.

            sage: from sage.topology.dehn_thurston_tt import DehnThurstonTT
            sage: tt = DehnThurstonTT([[1, 6, 5], [-1, 4, -6], [-5, -4, 2], [-8, -7, -2], [7, 9, 3], [-9, 8, -3]], [100, 20, 30, 1, 1, 4, 2, 2, 1])
            sage: tt.unzip_fold_first_move(1)
            sage: tt._gluing_list
            [[1, 5, 6], [4, -1, -6], [-5, -4, 2], [-8, -7, -2], [7, 9, 3], [-9, 8, -3]]
            sage: tt._measure
            [99, 20, 30, 1, 1, 5, 2, 2, 1]
            sage: tt.unzip_fold_first_move(-3)
            sage: tt._gluing_list
            [[1, 5, 6], [4, -1, -6], [-5, -4, 2], [-7, -8, -2], [9, 3, 7], [-9, 8, -3]]       
            sage: tt._measure
            [99, 22, 28, 1, 1, 5, 2, 2, 3]
            sage: tt.unzip_fold_first_move(-3,inverse=True)
            sage: tt._gluing_list
            [[1, 5, 6], [4, -1, -6], [-5, -4, 2], [-8, -7, -2], [7, 9, 3], [-9, 8, -3]]
            sage: tt._measure
            [99, 20, 30, 1, 1, 5, 2, 2, 1]
            sage: tt.unzip_fold_first_move(1,inverse=True)
            sage: tt._gluing_list
            [[1, 6, 5], [-1, 4, -6], [-5, -4, 2], [-8, -7, -2], [7, 9, 3], [-9, 8, -3]]
            sage: tt._measure
            [100, 20, 30, 1, 1, 4, 2, 2, 1]

        
        Next we test the cases where the unzippings don't go into the pants
        curve.

            sage: tt = DehnThurstonTT([[1, 6, 5], [-1, 4, -6], [-5, -4, 2], [-8, -7, -2], [7, 9, 3], [-9, 8, -3]], [3, 20, 3, 10, 10, 4, 15, 15, 1])
            sage: tt.unzip_fold_first_move(1)
            sage: tt._gluing_list
            [[1, 6], [4, -6], [-1, -5, -4, 5, 2], [-8, -7, -2], [7, 9, 3], [-9, 8, -3]]
            sage: tt._measure
            [3, 20, 3, 3, 7, 7, 15, 15, 1]
            sage: tt.unzip_fold_first_move(-3)
            sage: tt._gluing_list
            [[1, 6], [4, -6], [-1, -5, -4, 5, 2], [-3, 7, -8, -7, -2], [9, 3], [-9, 8]]
            sage: tt._measure
            [3, 23, 3, 3, 7, 7, 12, 3, 4]

        Now we choose a train track with lamda_11s instead of lambda23s and
        first test the unzippings into the pants curve.

            sage: tt = DehnThurstonTT([[1, 5], [-1, 4], [2, -8, 9, -7, -9], [-2, -5, 6, -4, -6], [7, 3], [8, -3]], [100, 20, 30, 1, 1, 4, 4, 4, 1])
            sage: tt.unzip_fold_first_move(1)
            sage: tt._gluing_list
            [[1, 5, -4], [-6, -1, 4], [2, -8, 9, -7, -9], [-2, -5, 6], [7, 3], [8, -3]]
            sage: tt._measure
            [99, 16, 30, 1, 5, 5, 4, 4, 1]
            sage: tt.unzip_fold_first_move(-3)
            sage: tt._gluing_list
            [[1, 5, -4], [-6, -1, 4], [2, -9, -8], [-2, -5, 6], [7, 3, 9], [-7, 8, -3]]
            sage: tt._measure
            [99, 11, 26, 1, 5, 5, 4, 5, 5]

        Finally, the same train track with a different measure so that the
        unzippings do not go into the pants curves.

            sage: tt = DehnThurstonTT([[1, 5], [-1, 4], [2, -8, 9, -7, -9], [-2, -5, 6, -4, -6], [7, 3], [8, -3]], [3, 20, 3, 10, 10, 13, 15, 15, 8])
            sage: tt.unzip_fold_first_move(1)
            sage: tt._gluing_list
            [[1, -4], [-6, 4], [2, -8, 9, -7, -9], [-2, -1, -5, 6, 5], [7, 3], [8, -3]]
            sage: tt._measure
            [16, 7, 3, 3, 7, 16, 15, 15, 8]
            sage: tt.unzip_fold_first_move(-3)
            sage: tt._gluing_list
            [[1, -4], [-6, 4], [-1, -5, 6, 5, 2], [-9, 7, -8, -7, -2], [3, 9], [-3, 8]]
            sage: tt._measure
            [16, 4, 3, 3, 7, 16, 12, 11, 11]

        """
        # p = pants_decomposition

        # # choosing the appropriate orientation of the switch (right side should
        # # have index 1 greater than the left side in the pants decomposition)
        # left = p.bdy_index_left_of_pants_curve(pants_curve)
        # right = p.bdy_index_left_of_pants_curve(-pants_curve)

        # if right == (left+1)%3:
        #     switch = pants_curve
        # else:
        #     switch = -pants_curve
        switch = self.orientation_of_switch_first_move(switch)        
        turning = self.get_turning(switch)
        twist_sign = -1 if inverse else 1
        bdy_switch = self.torus_boundary_switch(switch)
        # bdy_curve = p._torus_boundary_curve(switch)[0]
        # TODO: all this so far can be done intrinsically, without
        # pants_decomposition!
        
        # bdy_turning = self.get_turning(bdy_curve)
        lamb23 = len(self.outgoing_branches(switch)) == 3

        debug = False
        if debug:
            print "--------------------------------"
            print "BEGIN: unzip_fold_first_move()"
            print "--------------------------------"
            print "Switch:", switch
            print "Turning:", "LEFT" if turning == LEFT else "RIGHT"
            print "Lambda_23" if lamb23 else "Lambda_11"
            print "bdy_switch", bdy_switch
            print "Inverse:", inverse
        unzip_pos = self.unzip_with_collapse(switch,0,UP,branch_map,
                                             start_side=(turning+1)%2)

        if debug:
            print "Unzip pos:", unzip_pos
            print "Gluing list:", self._gluing_list
            print "Measure:", self._measure
            print "Outgoing branches in positive direction:", \
                self.outgoing_branches(switch)
            print "Outgoing branches in negative direction:", \
                self.outgoing_branches(-switch)

        # The inverse works in cases A, B, E
        # Doesn't work for C, D, F, G, and probably H
        
        if unzip_pos == 0:
            if lamb23:
                if (turning == LEFT) == (not inverse):
                    if debug:
                        print "A"
                    self.fold(-switch,1,2,start_side=turning)
                else:
                    if debug:
                        print "B"
                    self.fold(switch,1,0,(turning+1)%2)
                    self.unzip_fold_general_twist(bdy_switch,twist_sign,0)
            else:
                if (turning == LEFT) == (not inverse):
                    if debug:
                        print "C"
                        print "Gluing list:", self._gluing_list
                        print "Measure:", self._measure
                    self.unzip_fold_general_twist(bdy_switch,twist_sign,0)
                    if debug:
                        print "Gluing list:", self._gluing_list
                        print "Measure:", self._measure
                    self.fold_left_of_pants_curve(bdy_switch,0,1,inverse)
                    self.fold_left_of_pants_curve(bdy_switch,2,1,inverse)
                else:
                    if debug:
                        print "D"
                    self.unzip_fold_general_twist(bdy_switch,2*twist_sign,0)
                    self.fold_left_of_pants_curve(bdy_switch,3,2,inverse)
                    self.fold_left_of_pants_curve(bdy_switch,0,1,inverse)

        elif unzip_pos == 1:
            if lamb23:
                if (turning == LEFT) == (not inverse):
                    if debug:
                        print "E"
                    self.fold(-switch,0,1,turning)
                else:
                    if debug:
                        print "F"
                    self.fold(switch,1,0,(turning+1)%2)
                    self.unzip_fold_general_twist(bdy_switch,twist_sign,0)
            else:
                if (turning == LEFT) == (not inverse):
                    if debug:
                        print "G"
                    self.unzip_fold_general_twist(bdy_switch,twist_sign,0)
                    self.fold_left_of_pants_curve(bdy_switch,0,1,inverse)
                    self.fold_left_of_pants_curve(bdy_switch,3,2,inverse)
                else:
                    if debug:
                        print "H"
                    self.unzip_fold_general_twist(bdy_switch,2*twist_sign,0)
                    if debug:
                        print "Gluing list:", self._gluing_list
                        print "Measure:", self._measure
                        
                    self.fold_left_of_pants_curve(bdy_switch,4,3,inverse)
                    self.fold_left_of_pants_curve(bdy_switch,0,1,inverse)

        # new_turning = self.get_turning(switch)
        # print new_turning
        # new_pants_branch = self.outgoing_branch(switch,0,start_side=new_turning)

        # if abs(self.outgoing_branch(switch,0)) == \
        #    abs(self.outgoing_branch(-switch,0)):
        #     new_pants_branch = self.outgoing_branch(switch,0)
        # else:
        #     new_pants_branch = self.outgoing_branch(switch,0,RIGHT)

        # print switch
        # print new_pants_branch
            
        # self.swap_branch_numbers(switch,sign(switch)*abs(new_pants_branch))
                    
    
    def fold_left_of_pants_curve(self, bdy_switch, folded_branch_index,
                                 fold_onto_index, inverse=False):
        """
        Fold on the left of a pants curve.

        The input indices are the indices among only the outgoing branches on
        the left. In other words, the pants curve itself is not indexed. The
        indexing goes from bottom to top.
        """
        start_side = RIGHT if inverse else LEFT
        if self.get_turning(bdy_switch) == RIGHT:
            self.fold(bdy_switch, folded_branch_index, fold_onto_index, start_side)
        else:
            # print self.outgoing_branches(-bdy_switch)
            # print self.outgoing_branch(-bdy_switch, folded_branch_index+1)
            # print self.outgoing_branch(-bdy_switch, fold_onto_index+1)
            self.fold(-bdy_switch, folded_branch_index+1, fold_onto_index+1, start_side)




    
    # def unzip(self,switch,pos,unzip_pos,collapse,central_split=False,debug=False):
    #     r"""

    #     EXAMPLES:

    #     The train track for the first elementary move, when `t_1>0` and
    #     `\lambda_{23}` is present.
    #     Performing the unzipping according to `r<t_1`.

    #     #     sage: tt = TrainTrack([[-1,2,3], [-2,4,-3], [5], [-5,-4,1] ])
    #     #     sage: LEFT_UP = 0
    #     #     sage: tt.unzip(1,0,2,LEFT_UP)
    #     #     sage: tt._gluing_list
    #     #     [[2, -1, 3], [-2, 4, -3], [5], [-5, -4, 1]]
    #     #     sage: tt._branch_endpoint
    #     #     [[-2, 1, 1, -1, 2], [1, -1, -1, -2, -2]]

    #     # Now performing the unzipping according to `r>t_1`.

    #     #     sage: tt = TrainTrack([[-1,2,3], [-2,4,-3], [5], [-5,-4,1] ])
    #     #     sage: LEFT_UP = 0
    #     #     sage: tt.unzip(1,0,1,LEFT_UP)
    #     #     sage: tt._gluing_list
    #     #     [[2, 3], [-2, 4], [5], [-5, -1, -4, 1, -3]]
    #     #     sage: tt._branch_endpoint
    #     #     [[-2, 1, 1, -1, 2], [-2, -1, -2, -2, -2]]
        
    #     # The train track for the first elementary move, when ``t_1<0`` and
    #     # ``\lambda_{23}`` is present.
    #     # Performing the unzipping according to `r<t_1`.

    #     #     sage: tt = TrainTrack([[1,-2,3], [-1,-4,2], [5], [-5,-3,4] ])
    #     #     sage: RIGHT_UP = 1
    #     #     sage: tt.unzip(1,-1,0,RIGHT_UP)
    #     #     sage: tt._gluing_list
    #     #     [[1, 3, -2], [-1, -4, 2], [5], [-5, -3, 4]]
    #     #     sage: tt._branch_endpoint
    #     #     [[1, -1, 1, -2, 2], [-1, 1, -2, -1, -2]]

    #     # Now performing the unzipping according to `r>t_1`.

    #     #     sage: tt = TrainTrack([[1,-2,3], [-1,-4,2], [5], [-5,-3,4] ])
    #     #     sage: RIGHT_UP = 1
    #     #     sage: tt.unzip(1,-1,1,RIGHT_UP)
    #     #     sage: tt._gluing_list
    #     #     [[1, -2], [-4, 2], [5], [-5, -1, -3, 4, 3]]
    #     #     sage: tt._branch_endpoint
    #     #     [[1, -1, -2, -2, 2], [-2, 1, -2, -1, -2]]

    #     # The next train track is a has a left-twisting annulus. We perform an
    #     # unzip not next to the core curve of the annulus but in the next cusp
    #     # that goes into the core curve.

    #     #     sage: tt = TrainTrack([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]])
    #     #     sage: LEFT_DOWN = 2
    #     #     sage: tt.unzip(1,1,0,LEFT_DOWN)
    #     #     sage: tt._gluing_list
    #     #     [[1, 3, 4, 2], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]]
    #     #     sage: tt._branch_endpoint
    #     #     [[1, 1, 1, 1, 2, 3, 4], [-1, -2, -3, -4, -1, -1, -1]]
      
    #     # Now we unzip at the same cusp, going into the third branch on the other
    #     # side:: 

    #     #     sage: tt = TrainTrack([[1, 2, 3, 4], [-1, -5, -6, -7], [5], [-2], [6], [-3], [7], [-4]])
    #     #     sage: LEFT_TWO_SIDED = 4
    #     #     sage: tt.unzip(1,1,2,LEFT_TWO_SIDED)
    #     #     sage: tt._gluing_list
    #     #     [[3, 4, 2], [-6, -7, -5, -1], [5], [-2], [6, 1], [-3], [7], [-4]]
    #     #     sage: tt._branch_endpoint
    #     #     [[3, 1, 1, 1, 2, 3, 4], [-1, -2, -3, -4, -1, -1, -1]]



    #     """



    #     if collapse == LEFT_UP:
    #         assert(pos==0)
    #     elif collapse == RIGHT_UP:
    #         assert(pos==-1)
    #     elif collapse == LEFT_DOWN:
    #         assert(unzip_pos == 0)
    #     elif collapse == RIGHT_DOWN:
    #         assert(unzip_pos == -1)
    #     elif collapse == LEFT_TWO_SIDED:
    #         assert(unzip_pos > 0 or central_split)
    #     elif collapse == RIGHT_TWO_SIDED:
    #         assert(unzip_pos < -1 or central_split)

    #     unzip_branch = self.outgoing_branches(-switch)[unzip_pos]
    #     bottom_switch = self.branch_endpoint(unzip_branch)
    #     if -switch == bottom_switch and unzip_pos > end_index:
    #         unzip_pos += 1

    #     if debug:
    #         print "Unzip branch: ", unzip_branch
    #         print "Bottom switch: ", bottom_switch
    #         print "Corrected unzip_pos:", unzip_pos

    #     # dealing with collapsed branches
    #     if collapse in [LEFT_UP,RIGHT_UP]:
    #         # cut the collapsed branch off the starting switch and gluing it to
    #         # the bottom switch
    #         collapsed_branch = self.outgoing_branches(switch).pop(pos)

    #         # we do this after the pop in case bottom_switch == switch
    #         end_index = self.outgoing_branches(bottom_switch).index(-unzip_branch)            
    #         if debug:
    #             print "End index:", end_index
    #             print "Collapsed branch:", collapsed_branch
    #         assert(collapsed_branch != -unzip_branch)
    #         if not central_split:
    #             insert_pos = end_index if collapse == LEFT_UP else \
    #                          end_index + 1
    #             if debug:
    #                 print "Insert pos:", insert_pos
    #             self.outgoing_branches(bottom_switch).insert(insert_pos,
    #                                                        collapsed_branch)
    #     elif collapse in [LEFT_DOWN,RIGHT_DOWN]:
    #         end_index = self.outgoing_branches(bottom_switch).index(-unzip_branch)          
    #         assert(not central_split)
    #         # make sure unzipping does cycle back to the isotoped part
    #         if collapse == LEFT_DOWN:
    #             assert(end_switch != switch or end_index <= pos)
    #         else:
    #             assert(end_switch != switch or end_index > pos)
    #         # nothing to do
    #         pass
    #     elif collapse in [LEFT_TWO_SIDED,RIGHT_TWO_SIDED]:
    #         end_index = self.outgoing_branches(bottom_switch).index(-unzip_branch)            
    #         if collapse == LEFT_TWO_SIDED:
    #             collapsed_branch = self.outgoing_branches(switch).pop(0)
    #             assert(self.outgoing_branches(switch)[0] ==
    #                    -self.outgoing_branches(-switch)[0])
    #             self.outgoing_branches(-switch).pop(0)
    #             pos -= 1
    #             unzip_pos -= 1 # TODO: doesn't work for central splits
    #         else:
    #             collapsed_branch = self.outgoing_branches(switch).pop(-1)
    #             assert(self.outgoing_branches(switch)[-1] ==
    #                    -self.outgoing_branches(-switch)[-1])
    #             self.outgoing_branches(-switch).pop(-1)


                
    #     # move branches
    #     if collapse in [LEFT_UP,RIGHT_UP]:
    #         bottom_branches = self.outgoing_branches(-switch)
    #         if collapse == LEFT_UP:
    #             branches_to_move = bottom_branches[unzip_pos+1:]
    #             del bottom_branches[unzip_pos+1:]
    #         elif collapse == RIGHT_UP:
    #             branches_to_move = bottom_branches[:unzip_pos]
    #             del bottom_branches[:unzip_pos]
    #         top_switch = self.branch_endpoint(collapsed_branch)
    #         k = self.outgoing_branches(top_switch).index(-collapsed_branch)
    #         if collapse == LEFT_UP:
    #             insert_pos = k+1
    #         else:
    #             insert_pos = k
    #         if central_split:
    #             # remove collapsed_branch from the train track
    #             self.outgoing_branches(top_switch).pop(k)
    #             if collapse == LEFT_UP:
    #                 insert_pos = k
    #         self.outgoing_branches(top_switch)[insert_pos:insert_pos] = \
    #                                                     branches_to_move
    #         # set endpoints
    #         if central_split:
    #             self._set_endpoint(collapsed_branch,0)
    #             self._set_endpoint(-collapsed_branch,0)
    #         else:
    #             self._set_endpoint(-collapsed_branch,bottom_switch)
    #         for branch in branches_to_move:
    #             self._set_endpoint(-branch,top_switch)

                
    #     elif collapse in [LEFT_DOWN,RIGHT_DOWN]:
    #         top = self.outgoing_branches(switch)
    #         end = self.outgoing_branches(switch)[pos+1:]
    #         begin = self.outgoing_branches(switch)[:pos+1]
    #         k = self.outgoing_branches(bottom_switch).index(-unzip_branch)
    #         if collapse == LEFT_DOWN:
    #             branches_to_move = end
    #             del top[pos+1:]
    #             insert_pos = k+1
    #         else:
    #             branches_to_move = begin
    #             del top[:pos+1]
    #             insert_pos = k

    #         top_list = self.outgoing_branches(top_switch)
    #         top_list[insert_pos:insert_pos] = branches_to_move
            
    #         for branch in branches_to_move:
    #             self._set_endpoint(-branch,bottom_switch)
 

    #     elif collapse in [LEFT_TWO_SIDED,RIGHT_TWO_SIDED]:
    #         top = self.outgoing_branches(switch)
    #         n = len(top)
    #         top.insert(0,top[pos:])
    #         del top[n:]
    #         bottom = self.outgoing_branches(-switch)
    #         n = len(bottom)
    #         bottom.insert(0, bottom[unzip_pos:])
    #         del bottom[n:]
    #         bottom.append(collapsed_branch)
            
    #         k = self.outgoing_branches(bottom_switch).index(-unzip_branch)
    #         self.outgoing_branches(bottom_switch).insert(k+1,
    #                                         -collapsed_branch)

    #         self._set_endpoint(collapsed_branch,-switch)
    #         self._set_endpoint(-collapsed_branch,bottom_switch)


def unzip_sequence_mapping_class(tt_map,pants_decomposition,mapping_class):
    r"""Perform unzips determined by a mapping class.

    We are handed a train track map whose domain `\mu` is any measured train
    track and whose codomain `\tau` is a Dehn-Thurston train track for some
    pants decomposition. We are also handed a mapping class `f`.

    The goal is to perform (a minimal sequence of) unzips on `\mu`
    and `\tau` to get train tracks `\mu'` and
    `\tau'`. The unzipping sequences are required to satisfy the
    following:
    - `\mu` is unzipped according to its measure and `\mu'` is a
    maximal train track (hence it is possible that non-canonical
    choices have to be made)
    - `\tau'` carries `\mu'`
    - there exists another Dehn-Thurston train track `\tau_0` for the
    same pants decomposition as '\tau` such
    that `f(\tau')` is carried on `\tau_0`,

    The method modifies the train track map from `\mu` to `\tau`
    and does not make copies. This has three separate parts:
    1. Modifying `\mu`
    2. Modifying `\tau`
    3. Modifying the ``CarryingData``

    The method creates a `\tau_0` and the ``CarryingData`` between
    `f(\tau)'` and `\tau`_0` and returns them.

    INPUT:

    - ``tt_map`` -- a TrainTrackMap whose codomain is a
      Dehn-Thurston train track (TrainTrackInPants) and whose domain is a measured train track

    - ``pants_decomposition`` -- the pants decomposition of the
      Dehn-Thurston train track

    - ``mapping_class`` -- a list of DehnTwists, encoding a product of
      powers of Dehn twists, read left to right

    OUTPUT:

    a Dehn-Thurston train track (`\tau_0`) and the ``CarryingData``
    for `f(\tau)` being carried on `\tau_0`.


    """
    dom = tt_map.domain
    cod = tt_map.codomain
    p = pants_decomposition

    for twist in dehn_twists:
        # changing the pants decomposition
        for move in twist.elementary_moves:
            dt_tt, cdata = \
                unzip_sequence_elementary_move(tt_map, p, move)
            # p is now the pants decomposition after the elementary
            # move. Both the domain and the codomain of tt_map are
            # changed by unzipping
            
            tt_map = TrainTrackMap(dom, dt_tt,
                                   cdata*tt_map.carrying_data)

        # applying the twist
        dt_tt, cdata = \
                unzip_sequence_pants_twist(tt_map, p,
                                           twist.pants_curve,
                                           twist.power)

        tt_map = TrainTrackMap(dom, dt_tt,
                               cdata*tt_map.carrying_data)

        # changing back the pants decomposition
        for move in reversed(twist.elementary_moves):
            dt_tt, cdata = \
                unzip_sequence_elementary_move(tt_map, p, move)
            
            tt_map = TrainTrackMap(dom, dt_tt,
                                   cdata*tt_map.carrying_data)

            # WARNING: this is probably wrong for type 1 elementary moves,
            # because applying a type 1 elementary move on the same
            # curve twice does not result in the identity (the cyclic
            # orientation in the pair of pants is reversed. So for
            # type 1 moves, the above two line may need to be
            # called three times in order to get the inverse.

    return dt_tt, cdata




def unzip_sequence_elementary_move(tt_map,pants_decomposition,
                                   pants_curve):
    r"""Perform unzips determined by an elementary move on the pants decomposition.

    Same as ``unzip_sequence_mapping_class``, but instead of a mapping
    class, now we have an elementary move a pants decomposition.

    Here `\tau_0` is a Dehn-Thurston train track of the new pants
    decomposition and we want `\tau'` to be carried on `\tau_0`.

    INPUT:

    - ``tt_map`` -- 

    - ``pants_decomposition`` -- 

    - ``pants_curve`` -- the index of the pants curve on which the
      elementary move is performed

    OUTPUT:

    a Dehn-Thurston train track (`\tau_0`) which is TrainTrackInPants
    object and the ``CarryingData`` for `f(\tau)` being carried on
    `\tau_0`.

    """
    pass



