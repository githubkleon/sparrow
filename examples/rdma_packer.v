module rdma_packer(
input  wire clk,
input  wire rst,

//Input AXI Stream Interface
input  wire [63   : 0]    data_slave,
input  wire [7    : 0]    keep_slave,
input  wire [0    : 0]    valid_slave,
input  wire [0    : 0]    last_slave,
output wire [0    : 0]    ready_slave,

//Output AXI Stream Interface
output wire [63   : 0]    data_master,
output wire [7    : 0]    keep_master,
output wire [0    : 0]    valid_master,
output wire [0    : 0]    last_master,
input  wire [0    : 0]    ready_master,

//Input results
input  wire [15   : 0]    src_port,
input  wire [15   : 0]    dst_address,
input  wire [15   : 0]    length,
input  wire [15   : 0]    checksum
);

localparam IDLE = 4'b0001,
               HEAD = 4'b0010,
               DATA = 4'b0100,
               WAIT = 4'b1000;
    
    reg [3:0] ps;
    reg [3:0] ns;
    
    wire is_idle;
    wire is_head;
    wire is_data;
    wire is_wait; 
    
    assign is_idle = (ps == IDLE);
    assign is_head = (ps == HEAD);
    assign is_data = (ps == DATA);
    assign is_wait = (ps == WAIT);

reg  [63  :0] temp_data;
    reg  [7   :0] keep_out;
    wire [0   :0] valid_out;
    wire [0   :0] last_out;
    wire [0   :0] ready_out;

reg  [63  :0] data;
    reg  [0   :0] valid;
    reg  [0   :0] last;
reg  [15  :0] length;
reg  [3   :0] header;
wire [63  :0] rdata;
wire [63  :0] data_slave_rev;
wire header_last;
    assign header_last = (header == 'd0);


    assign valid_out = is_head | (is_data & valid) | last;
    assign last_out  = is_data & (length <= 'd8  ) & valid_out;
    assign ready_slave = ready_out & ~last;

    assign data_master  = rdata;
    assign valid_master = valid_out;
    assign keep_master  = keep_out;
    assign last_master  = last_out;
    assign ready_out = (ns == HEAD) ? 0 : ready_master;

always @ (*)
        begin 
            keep_out = 0;
            case (length)
        'd7  : keep_out =   8'h7f;
        'd6  : keep_out =   8'h3f;
        'd5  : keep_out =   8'h1f;
        'd4  : keep_out =   8'h0f;
        'd3  : keep_out =   8'h07;
        'd2  : keep_out =   8'h03;
        'd1  : keep_out =   8'h01;
        'd0  : keep_out =   8'h00;
        default: keep_out =   8'hff;
            endcase
        end
        
assign data_slave_rev = {
data_slave[7   :   0],
data_slave[15  :   8],
data_slave[23  :  16],
data_slave[31  :  24],
data_slave[39  :  32],
data_slave[47  :  40],
data_slave[55  :  48],
data_slave[63  :  56]
};

assign rdata = {
temp_data[7   :   0],
temp_data[15  :   8],
temp_data[23  :  16],
temp_data[31  :  24],
temp_data[39  :  32],
temp_data[47  :  40],
temp_data[55  :  48],
temp_data[63  :  56]
};

wire valid_ready_m;
    assign valid_ready_m = valid_slave & ready_master;
    
    wire valid_ready_s;
    assign valid_ready_s = valid_slave & ready_slave;
    
    wire true_last;
    assign true_last = last_slave & valid_ready_s;
    
always @(posedge clk or posedge rst) 
    begin
        if (rst) ps <= IDLE;
        else     ps <= ns;
    end

always @ (*)
    begin
        case (ps)
            IDLE:   if  (valid_slave)   ns = HEAD;
                    else                ns = IDLE;
            HEAD:   if  (ready_master & header_last)
                                        ns = DATA;
                    else                ns = HEAD;
            DATA:   if (last_out & ready_master) 
                    begin
                        if (last)       ns = IDLE;
                        else            ns = WAIT;
                    end
                    else                ns = DATA;
            WAIT:   if (true_last)      ns = IDLE;
                    else                ns = WAIT;
            default:                    ns = IDLE;
        endcase
    end

always @ (posedge clk)
    begin 
        if (valid_ready_s) begin
            data <= data_slave_rev;
        end
        else begin
            data <= data;
        end
    end
    
    always @ (posedge clk or posedge rst)
    begin
        if (rst)
            valid <= 'b0;
        else if (ready_master) 
            valid <= valid_ready_s;
        else
            valid <= valid;
    end
    
    always @ (posedge clk or posedge rst)
    begin
        if (rst)
            last <= 1'b0;
        else if (true_last)
            last <= 1'b1;
        else if (ns == IDLE)
            last <= 1'b0;
        else
            last <= last;
    end
    
    always @ (*)
    begin
        temp_data = 'd0;
        case (ps)
        HEAD:
            case (header)
                'd0   : 
                begin
                    temp_data[63:48] = src_port[15:0];         
                    temp_data[47:32] = dst_address[15:0];      
                    temp_data[31:16] = length[15:0];           
                    temp_data[15:0] = checksum[15:0];         
                end
            endcase

        DATA:
            temp_data = data[63:0];
        endcase
    end

always @ (posedge clk or posedge rst)
    begin
        if (rst) 
            length <= 'd0;
        else if (ns == HEAD)
            length <= length;
        else if (is_data & valid_out & ready_master)
            length <= length - 'd8;
        else if (ns == IDLE) 
            length <= 'd0;
        else 
            length <= length;
    end

always @(posedge clk or posedge rst) begin
        if (rst) 
            header <= 'd0;
        else if (~is_head)
            header <= 'd0;
        else if (ready_master)
            header <= header + 'd1;
        else
            header <= header;
    end
    
    endmodule